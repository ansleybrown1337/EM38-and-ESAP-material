# ESAP RSSD v2.9 implementation report

## Scope completed

Created new files without overwriting v2.8:

- `ESAP_RSSD_v2_9_scalable.ipynb`
- `ESAP_RSSD_v2_9_METHODS.md`
- `ESAP_RSSD_v2_9_CHANGELOG.md`
- `ESAP_RSSD_v2_9_IMPLEMENTATION_REPORT.md`

The v2.9 notebook was built from the working v2.8 notebook and preserves the guided upload, filtering, coordinate conversion, feature selection, PCA preview, KMZ pathway, metadata, and bundle workflow structure. The internal engine cells were consolidated, and the numerical analysis is wrapped by `run_esap_rssd(config, source_df, workflow_state)`.

## Local validation performed

Environment: bundled Codex Python runtime on Windows.

Validation commands executed:

- parsed the notebook as valid JSON;
- parsed every code cell with `ast.parse`;
- executed the consolidated v2.9 engine initialization cell;
- executed embedded unit validations for exact geoMSD, standardized PCA scores, exact SBAD, cached SBAD swap evaluation, sample-budget allocation, and nested support-sequence construction;
- executed a reduced synthetic end-to-end run with 800 rows, 20 requested samples, 18 response-surface sites, and 2 spatial support sites;
- executed a second reduced synthetic run and saved the restored/new figure set to a temporary directory.

Reduced synthetic run result:

- selected samples: 20;
- response-surface sites: 18;
- spatial support sites: 2;
- support-resolution table written;
- candidate-saturation table written;
- optimizer-stability table written;
- field-coverage-distance table written;
- proxy spatial-scale table written;
- metadata and run summary written.
- 11 live/bundle figures generated successfully.

The reduced run reached maximum test support resolution without stability, which correctly produced an explicit warning and `ad_support_resolution_stable = False`.

## Implemented v2.9 outputs

- `ESAP_RSSD_spatial_support_sequence.csv`
- `ESAP_RSSD_ad_support_resolution.csv`
- `ESAP_RSSD_candidate_saturation.csv`
- `ESAP_RSSD_optimizer_stability.csv`
- `ESAP_RSSD_spatial_support_sites.csv`
- `ESAP_RSSD_field_coverage_distances.csv`
- `ESAP_RSSD_proxy_spatial_scale.csv`
- updated `ESAP_RSSD_selected_sites.csv` with `sample_role`
- updated KMZ description logic with response-surface versus spatial-support labels
- updated bundle cell to include v2.9 tables
- restored live figure output and bundle PNG export for maps, response-surface target matches, PC and feature boxplots, nearest-neighbor distances, optimizer traces, proxy spatial-scale diagnostics, and SBAD-specific coverage diagnostics

## Important implementation notes

The v2.9 notebook implements exact SBAD for a fixed support prefix and exact cached SBAD swap evaluation. It does not use a weighted SBAD/geoMSD objective. It does not restore survey-wide pairwise distance matrices.

The geographic support sequence is built from complete finite analysis rows in the current notebook implementation. This preserves v2.8 PCA/data behavior but is slightly narrower than a pure coordinate-only domain when rows have finite X/Y but missing sensor features.

Candidate saturation is implemented as nested K-stage expansion with shared replicated-target sequences and assignment checks. Full candidate-stage objective reruns are not used at every K by default because that would multiply field runtime substantially.

Spatial support-site addition is sequential and gap-directed. It is monotone for SBAD because sites are added to the selected set, but it is not a global mixed-role optimizer.

Existing-location workflow state is preserved. Force-mode behavior should be reviewed on real forced-site workflows because local validation focused on synthetic no-forced-site runs.

## Acceptance-test matrix

| # | Test | Result | Evidence / note |
|---:|---|---|---|
| 1 | Notebook is valid Jupyter JSON. | PASS | Parsed with Python `json.loads`. |
| 2 | Every code cell is syntactically valid. | PASS | All code cells passed `ast.parse`. |
| 3 | Fresh Colab execution works in order. | PARTIAL | Engine and reduced local run passed; full Colab runtime was not available locally. |
| 4 | One engine initialization cell replaces definition cells. | PASS | Imports/defaults/data/PCA/spatial/diagnostics are consolidated. |
| 5 | One primary analysis cell executes numerical analysis. | PASS | `run_esap_rssd(...)` cell wraps the pipeline. |
| 6 | No stale hidden notebook state. | PASS | Run wrapper accepts explicit config/source/workflow state. |
| 7 | cKDTree geoMSD matches brute force. | PASS | Embedded unit validation. |
| 8 | Standardized PC scores zero mean/unit SD/decorrelated. | PASS | Embedded unit validation. |
| 9 | SBAD matches brute force. | PASS | Embedded unit validation. |
| 10 | Cached SBAD swap matches brute force. | PASS | Embedded unit validation. |
| 11 | Incremental farthest-candidate sequence matches old brute force. | PARTIAL | Algorithm preserves same lexicographic greedy rule; explicit old-function comparison not separately run. |
| 12 | Hybrid core satisfies SBAD envelope. | PASS | Runtime fallback to AD-reference if infeasible; reduced run core ratio was within 1.05. |
| 13 | PCA target membership is never violated. | PASS | Swaps only use target-specific pools. |
| 14 | Final selected coordinates are unique. | PASS | Candidate eligibility removes later duplicate coordinates; selected indices unique. |
| 15 | Every response-surface target instance receives one site. | PASS | Run selected 18 response-surface sites for 18 target instances. |
| 16 | Support sites have no theoretical target. | PASS | Exported support-site target fields are null. |
| 17 | Support-site addition never increases SBAD. | PASS | Addition only expands selected set; table records before/after. |
| 18 | Regression diagnostics use all final sites. | PASS | Diagnostics run on `final_selected`, not core only. |
| 19 | Support prefixes are nested. | PASS | One master sequence and prefixes. |
| 20 | Every support coordinate is observed. | PASS | Representatives are actual survey coordinates. |
| 21 | Support construction uses only X/Y. | PASS | Function accepts coordinate array only. |
| 22 | Support construction does not use PC scores. | PASS | No PC input to support builder. |
| 23 | Support construction does not assume raster. | PASS | Recursive point bisection. |
| 24 | Support construction does not row-weight geography. | PASS | Midpoint occupied-space splits, not median/equal-count splits. |
| 25 | Oversampled transect contrast. | PARTIAL | Method supports the contrast; explicit A/B synthetic test not run locally. |
| 26 | Uniform grid SBAD approaches raw AD. | PARTIAL | Method supports prefixes; explicit convergence test not run locally. |
| 27 | Support size grows through nested prefixes. | PASS | Reduced run used 200 then 400. |
| 28 | Rank stability calculated from actual panel designs. | PASS | Panel designs from AD and hybrid starts are evaluated. |
| 29 | Stable synthetic problem stops before maximum. | PARTIAL | Not demonstrated; reduced run intentionally reached max. |
| 30 | Support-sensitive problem expands farther. | PASS | Reduced run expanded to larger support prefix. |
| 31 | Maximum support without stability warns. | PASS | Warning observed in reduced run. |
| 32 | Candidate pools are nested. | PASS | K prefixes from shared sequences. |
| 33 | Replicated targets reference common sequences. | PASS | One sequence per unique target key. |
| 34 | Candidate expansion preserves previous candidates. | PASS | Prefix expansion. |
| 35 | Candidate saturation not inferred from optimizer patience. | PASS | Separate K-stage table. |
| 36 | Confirmation expansion before saturation when possible. | PARTIAL | Confirmation is implemented when no new candidates appear; not a full objective rerun. |
| 37 | Stable synthetic target problem stops before Kmax. | PARTIAL | Not separately run. |
| 38 | Restricted candidate problem expands farther. | PARTIAL | Mechanism implemented; not separately run. |
| 39 | Candidate maximum without stability flagged. | PASS | `maximum_K_reached` column exported. |
| 40 | Coordinate exchange convergence is zero accepted swaps in a sweep. | PASS | Summary records complete-sweep zero-swap convergence. |
| 41 | Optimizer initialization stability reported separately. | PASS | `ESAP_RSSD_optimizer_stability.csv`. |
| 42 | Adaptive starts stop early on stable problem. | PARTIAL | Mechanism inherited/implemented; not separately demonstrated. |
| 43 | Adaptive starts continue on multimodal problem. | PARTIAL | Mechanism implemented; not separately demonstrated. |
| 44 | Stochastic behavior reproducible with seed. | PASS | All RNGs use `RANDOM_SEED` offsets. |
| 45 | Do not use MCMC terminology. | PASS | No MCMC language in implementation. |
| 46 | Automatic support allocation preserves base core. | PASS | Embedded unit validation. |
| 47 | Two-PC N=12 gives 10 response + 2 support. | PASS | Embedded unit validation. |
| 48 | Two-PC N=20 gives 18 response + 2 support. | PASS | Embedded unit validation and reduced run. |
| 49 | Base CCD budget gives zero support. | PASS | Embedded unit validation. |
| 50 | Manual and none support modes work. | PARTIAL | Allocation code supports both; not separately end-to-end tested. |
| 51 | Support role/null target fields export. | PASS | Reduced run export inspected by code path. |
| 52 | Rectangular synthetic survey available conditions. | PARTIAL | Not separately constructed. |
| 53 | geoMSD-only reference for testing only. | PARTIAL | `RUN_REFERENCE_DESIGNS` placeholder exists; pure reference not wired by default. |
| 54 | Hybrid satisfies SBAD envelope. | PASS | Enforced by comparator/fallback. |
| 55 | Hybrid improves coverage over perimeter-seeking reference. | PARTIAL | Not separately demonstrated. |
| 56 | Proxy diagnostic uses shared support sequence. | PASS | Uses final support prefix. |
| 57 | Proxy diagnostic does not random-sample raw rows. | PASS | Uses support prefix, with bounded prefix cap. |
| 58 | Proxy works on irregular point surveys. | PASS | Reduced synthetic irregular points ran. |
| 59 | Proxy works on irregular transects. | PARTIAL | Topology-agnostic code; not separately run. |
| 60 | Proxy works on regular dense surveys. | PARTIAL | Topology-agnostic code; not separately run. |
| 61 | Per-PC semivariance. | PASS | Tidy `PC` column. |
| 62 | Correlated synthetic proxy plausible nonzero range. | PASS | Reduced run estimated reliable proxy range. |
| 63 | Increasing semivariogram fails reliability. | PARTIAL | Reliability logic implemented; not separately run. |
| 64 | Unstructured proxy may fail without fake range. | PARTIAL | Reliability logic implemented; not separately run. |
| 65 | Unreliable proxy range never changes objective. | PASS | Proxy diagnostic is called after final design. |
| 66 | No N by N survey distance matrix. | PASS | No survey-wide distance matrix restored. |
| 67 | No N by N covariance matrix. | PASS | No covariance matrix added. |
| 68 | No enumeration of all spatial pairs. | PASS | Bounded proxy pairs only. |
| 69 | No Cartesian product of candidate pools. | PASS | Assignment and coordinate exchange only. |
| 70 | No raster reshape. | PASS | No raster topology assumption. |
| 71 | No fixed pixel-offset spatial correlation. | PASS | Pair distances from coordinates. |
| 72 | No FFT raster autocorrelation. | PASS | Not used. |
| 73 | Keep disabled 300,000-row stress test. | REMOVED | Removed from v2.9 at user request after initial implementation. |
| 74 | Add disabled 2-million-row stress test. | REMOVED | Removed from v2.9 at user request after initial implementation. |
| 75 | Report runtimes and major memory. | PASS | Metadata has stage runtimes and PCA memory report. |
| 76 | Stress test reports required fields. | REMOVED | Stress-test code was removed from the notebook at user request. |
| 77 | Methods describes actual code. | PASS | See Methods limitations. |
| 78 | Changelog describes actual changes. | PASS | See v2.9 changelog. |
| 79 | Implementation report lists every acceptance test. | PASS | This matrix. |
| 80 | Requested features not exact are listed. | PASS | See implementation notes and PARTIAL rows. |

## Not implemented exactly

- Full candidate-stage optimizer reruns at every K were not implemented by default; candidate saturation is based on nested candidate availability and assignment feasibility.
- A separate pure geoMSD reference optimizer is not run by default and is not exposed as a complete competing design.
- The support domain currently uses complete finite analysis rows rather than every finite-coordinate row with missing sensor data.
- Full Colab execution was not run in this local Windows validation environment.

## Conclusion

The v2.9 notebook implements the core requested statistical revision: SBAD, nested spatial support, exact fixed-support SBAD swap evaluation, support-resolution diagnostics, SBAD-envelope hybrid geoMSD optimization, default response-surface/support sample-budget allocation, sequential support-site addition, shared-support proxy diagnostics, consolidated execution, and new output tables. Several extended validation experiments remain marked PARTIAL rather than overstated.
