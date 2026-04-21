// Package phreeqc is a thin wrapper around the USGS PHREEQC command-line
// binary. It builds an input deck (or accepts one you already wrote), shells
// out to `phreeqc`, parses the tab-delimited SELECTED_OUTPUT file, and
// returns a typed result.
//
// Usage:
//
//	client, err := phreeqc.New(phreeqc.Config{
//	    Binary:   "phreeqc",
//	    Database: "/opt/homebrew/share/phreeqc/database/pitzer.dat",
//	    TempDir:  "",
//	})
//	if err != nil { panic(err) }
//
//	report, err := client.Run(deckString)
//	if err != nil { panic(err) }
//
//	for mineral, si := range report.SaturationIndices {
//	    fmt.Printf("%-12s SI = %+.2f\n", mineral, si)
//	}
//
// Notes:
//   - The wrapper does NOT install PHREEQC. Installation is up to the user
//     (brew, conda, or USGS distribution; see SKILL.md).
//   - The input deck must contain a SELECTED_OUTPUT block that writes to a
//     known path. This wrapper generates a temp path and rewrites the
//     `-file` line so the caller does not have to.
//   - Stdout / stderr from the phreeqc process are captured and returned on
//     error; this is the fastest way to surface convergence or parse errors.
package phreeqc

import (
	"bytes"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strconv"
	"strings"
)

// Config holds the runtime configuration for the PHREEQC wrapper.
type Config struct {
	// Binary is the path (or PATH-resolvable name) of the phreeqc executable.
	// Default: "phreeqc".
	Binary string

	// Database is the absolute path to a thermodynamic database file
	// (e.g. pitzer.dat, phreeqc.dat, llnl.dat). Required.
	Database string

	// TempDir is where input and output files are written. If empty, the
	// process-default temp directory is used. Files are deleted on success
	// unless KeepFiles is true.
	TempDir string

	// KeepFiles, if true, leaves the .pqi / .pqo / .sel / .log files on disk
	// after Run returns. Useful for debugging; false for production.
	KeepFiles bool
}

// Client is the PHREEQC runner.
type Client struct {
	cfg Config
}

// New constructs a Client and validates the binary and database paths.
func New(cfg Config) (*Client, error) {
	if cfg.Binary == "" {
		cfg.Binary = "phreeqc"
	}
	if _, err := exec.LookPath(cfg.Binary); err != nil {
		return nil, fmt.Errorf("phreeqc binary %q not found: %w", cfg.Binary, err)
	}
	if cfg.Database == "" {
		return nil, fmt.Errorf("database path is required")
	}
	if _, err := os.Stat(cfg.Database); err != nil {
		return nil, fmt.Errorf("database %q not accessible: %w", cfg.Database, err)
	}
	return &Client{cfg: cfg}, nil
}

// SIReport is a parsed SELECTED_OUTPUT row from a PHREEQC simulation.
type SIReport struct {
	// SaturationIndices maps mineral name to SI value (log10 IAP / Ksp).
	SaturationIndices map[string]float64

	// Molalities maps species name (e.g. "Li+", "SO4-2") to mol/kgw.
	Molalities map[string]float64

	// Totals maps element name to total dissolved concentration (mol/kgw).
	Totals map[string]float64

	// IonicStrength in mol/kgw. Zero if not requested in SELECTED_OUTPUT.
	IonicStrength float64

	// Temperature in deg C.
	Temperature float64

	// PH final pH.
	PH float64

	// Raw is the parsed SELECTED_OUTPUT row as a flat map of column to value.
	Raw map[string]string

	// Stdout captures the phreeqc process stdout (usually empty).
	Stdout string

	// OutputFile is the path to the long-form .pqo output for troubleshooting.
	// Empty if KeepFiles is false.
	OutputFile string
}

// Run executes PHREEQC with the given input deck. The deck should contain a
// SELECTED_OUTPUT block; if the `-file` path is not absolute, it will be
// rewritten to a temp path inside cfg.TempDir.
func (c *Client) Run(deck string) (*SIReport, error) {
	dir := c.cfg.TempDir
	if dir == "" {
		var err error
		dir, err = os.MkdirTemp("", "phreeqc-*")
		if err != nil {
			return nil, fmt.Errorf("mkdir temp: %w", err)
		}
		if !c.cfg.KeepFiles {
			defer os.RemoveAll(dir)
		}
	}

	pqi := filepath.Join(dir, "input.pqi")
	pqo := filepath.Join(dir, "output.pqo")
	sel := filepath.Join(dir, "selected.sel")
	logf := filepath.Join(dir, "run.log")

	// Rewrite SELECTED_OUTPUT -file directive to our temp path.
	deck = rewriteSelectedOutputFile(deck, sel)

	if err := os.WriteFile(pqi, []byte(deck), 0o644); err != nil {
		return nil, fmt.Errorf("write input deck: %w", err)
	}

	cmd := exec.Command(c.cfg.Binary, pqi, pqo, c.cfg.Database, logf)
	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr
	if err := cmd.Run(); err != nil {
		return nil, fmt.Errorf("phreeqc exit: %w; stderr: %s", err, stderr.String())
	}

	// Parse selected output.
	selBytes, err := os.ReadFile(sel)
	if err != nil {
		return nil, fmt.Errorf("read selected output %q: %w (check deck for SELECTED_OUTPUT block)", sel, err)
	}

	report, err := parseSelectedOutput(selBytes)
	if err != nil {
		return nil, fmt.Errorf("parse selected output: %w", err)
	}
	report.Stdout = stdout.String()
	if c.cfg.KeepFiles {
		report.OutputFile = pqo
	}
	return report, nil
}

var selectedFileLine = regexp.MustCompile(`(?m)^\s*-file\s+\S+`)

// rewriteSelectedOutputFile replaces the `-file <path>` line inside the
// SELECTED_OUTPUT block so the wrapper controls the output location.
func rewriteSelectedOutputFile(deck, targetPath string) string {
	replacement := "    -file           " + targetPath
	if selectedFileLine.MatchString(deck) {
		return selectedFileLine.ReplaceAllString(deck, replacement)
	}
	// No SELECTED_OUTPUT block file line. Caller error; return as-is and let
	// parseSelectedOutput produce a helpful error.
	return deck
}

// parseSelectedOutput reads a PHREEQC SELECTED_OUTPUT tab-delimited file and
// returns an SIReport derived from the first data row. If multiple simulations
// are present (e.g., SOLUTION + REACTION steps), only the last row is used;
// callers who need every step should parse the file manually.
func parseSelectedOutput(data []byte) (*SIReport, error) {
	lines := strings.Split(strings.TrimRight(string(data), "\n"), "\n")
	if len(lines) < 2 {
		return nil, fmt.Errorf("selected output has no data rows (only %d lines)", len(lines))
	}

	headers := splitTSV(lines[0])
	last := splitTSV(lines[len(lines)-1])
	if len(last) != len(headers) {
		return nil, fmt.Errorf("header/data column count mismatch: %d vs %d", len(headers), len(last))
	}

	r := &SIReport{
		SaturationIndices: map[string]float64{},
		Molalities:        map[string]float64{},
		Totals:            map[string]float64{},
		Raw:               map[string]string{},
	}

	for i, h := range headers {
		val := strings.TrimSpace(last[i])
		r.Raw[h] = val

		switch {
		case strings.HasPrefix(h, "si_"):
			if f, ok := parseFloat(val); ok {
				r.SaturationIndices[strings.TrimPrefix(h, "si_")] = f
			}
		case strings.HasPrefix(h, "m_"):
			if f, ok := parseFloat(val); ok {
				r.Molalities[strings.TrimPrefix(h, "m_")] = f
			}
		case strings.HasSuffix(h, "(mol/kgw)") || strings.HasPrefix(h, "t_"):
			// Totals often appear as element name with unit suffix, but
			// SELECTED_OUTPUT -totals actually produces bare element names.
			if f, ok := parseFloat(val); ok {
				name := strings.TrimPrefix(h, "t_")
				name = strings.TrimSuffix(name, "(mol/kgw)")
				r.Totals[strings.TrimSpace(name)] = f
			}
		case h == "mu":
			if f, ok := parseFloat(val); ok {
				r.IonicStrength = f
			}
		case h == "temp(C)" || h == "temp":
			if f, ok := parseFloat(val); ok {
				r.Temperature = f
			}
		case h == "pH":
			if f, ok := parseFloat(val); ok {
				r.PH = f
			}
		}
	}
	return r, nil
}

func splitTSV(line string) []string {
	// PHREEQC SELECTED_OUTPUT uses tabs; some versions pad with spaces.
	// Split on tabs and trim each field.
	parts := strings.Split(line, "\t")
	out := make([]string, len(parts))
	for i, p := range parts {
		out[i] = strings.TrimSpace(p)
	}
	return out
}

func parseFloat(s string) (float64, bool) {
	if s == "" || s == "-999.999" || s == "-9999" {
		return 0, false
	}
	f, err := strconv.ParseFloat(s, 64)
	if err != nil {
		return 0, false
	}
	return f, true
}

// ---------------------------------------------------------------------------
// Convenience: ready-to-run Smackover deck for smoke testing.
// ---------------------------------------------------------------------------

// SmackoverExampleDeck returns a PHREEQC input deck modeling a typical
// Smackover Fm produced water at reservoir conditions. Use for smoke testing
// the wrapper and for DLE screening demos.
func SmackoverExampleDeck() string {
	return `TITLE Smackover Fm brine - median high-Li DLE screen
SOLUTION 1
    temp      90
    pH        5.5
    pe        2.0
    redox     pe
    units     mg/l
    density   1.20
    Na        85000
    K         3500
    Ca        40000
    Mg        3000
    Sr        1500
    Ba        50
    Li        400
    Cl        180000  charge
    Alkalinity 50 as HCO3
    S(6)      200
    Br        5000
    B         200
    Fe(2)     30
SELECTED_OUTPUT
    -file           /tmp/placeholder.sel
    -reset          false
    -saturation_indices Barite Calcite Celestite Gypsum Anhydrite Halite \
                        Dolomite Strontianite Witherite
    -molalities     Li+ Mg+2 Ca+2 Ba+2 Sr+2 SO4-2
    -totals         Li Mg Ca Ba Sr S(6)
    -ionic_strength true
    -temperature    true
    -pH             true
END
`
}

// ---------------------------------------------------------------------------
// Example main (build tag excluded so it does not collide with callers).
// ---------------------------------------------------------------------------

/*
//go:build ignore

package main

import (
	"fmt"
	"log"
	"os"
	"sort"

	"example.com/phreeqc"
)

func main() {
	db := os.Getenv("PHREEQC_DB")
	if db == "" {
		db = "/opt/homebrew/share/phreeqc/database/pitzer.dat"
	}
	client, err := phreeqc.New(phreeqc.Config{Database: db})
	if err != nil {
		log.Fatal(err)
	}
	report, err := client.Run(phreeqc.SmackoverExampleDeck())
	if err != nil {
		log.Fatal(err)
	}
	names := make([]string, 0, len(report.SaturationIndices))
	for name := range report.SaturationIndices {
		names = append(names, name)
	}
	sort.Strings(names)
	fmt.Printf("Ionic strength: %.2f mol/kgw  (T=%.0f C, pH=%.2f)\n\n",
		report.IonicStrength, report.Temperature, report.PH)
	fmt.Println("Saturation indices:")
	for _, name := range names {
		fmt.Printf("  %-14s %+6.3f\n", name, report.SaturationIndices[name])
	}
}
*/
