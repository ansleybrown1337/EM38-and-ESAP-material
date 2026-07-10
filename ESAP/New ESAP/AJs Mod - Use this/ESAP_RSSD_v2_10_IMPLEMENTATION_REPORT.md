# ESAP RSSD v2.10 implementation report

## Scope completed

Corrected the existing v2.10 files in place:

- `ESAP_RSSD_v2_10_scalable.ipynb`
- `ESAP_RSSD_v2_10_METHODS.md`
- `ESAP_RSSD_v2_10_CHANGELOG.md`
- `ESAP_RSSD_v2_10_IMPLEMENTATION_REPORT.md`

No v2.10.1 notebook or new versioned file was created.

## Pre-field-run implementation audit and corrections

### Issue 1. Missing spatial support configuration fields

- **Reproduced:** PASS by inspection. The active support-site function referenced `SUPPORT_GAP_ANCHORS` and `SUPPORT_CANDIDATE_NEIGHBORS_PER_ANCHOR`, but `RSSDConfig` did not define them.
- **Correction implemented:** Added both fields to `RSSDConfig`, added validation requiring positive integers, and exposed them only in advanced support-site settings.
- **Validation performed:** Engine initialization, unit support-site exact-ranking test, and 850-row end-to-end run executed the support-site pathway without `AttributeError`.
- **Result:** PASS.

### Issue 2. Repeated tiny selected-set threaded cKDTree overhead

- **Reproduced:** PASS by development benchmark. The old selected-set cKDTree path was benchmarked for 10,000 repeated 20-site evaluations as development evidence; normal engine initialization no longer runs that benchmark.
- **Correction implemented:** Production selected-site nearest-neighbor distances, exact geoMSD, and minimum separation now use an exact vectorized `m` by `m` selected-set Euclidean distance array.
- **Validation performed:** Randomized selected sets of sizes 6, 10, 12, 20, and 40 matched scipy `pdist/squareform`; old cKDTree geoMSD matched the new method on small equality checks; minimum separation matched brute force. The 10,000-evaluation timing benchmark is now opt-in.
- **Result:** PASS.

Selected-set benchmark:

| Evaluations | Selected sites | Old cKDTree `workers=-1` seconds | New vectorized seconds | Speedup | Equality |
|---:|---:|---:|---:|---:|---|
| 10,000 | 20 | 22.9296506001 | 0.1073691000 | 213.5591208745x | PASS |

### Issue 3. Candidate-sequence geographic distances recomputed from scratch

- **Reproduced:** PASS by inspection and benchmark. The active candidate sequence recomputed the full remaining-candidates by retained-candidates distance block at each greedy step.
- **Correction implemented:** Candidate construction now maintains exact incremental `min_geo` and updates it only with distances to the newly retained candidate. New tolerance-shell observations are initialized exactly against the retained set.
- **Validation performed:** Single-tolerance and progressive-tolerance candidate sequences matched a brute-force reference exactly; prefix nesting was verified.
- **Result:** PASS.

Candidate-sequence benchmark:

| Neighborhood size | Kmax | Tolerance expansions | Old recompute seconds | New incremental seconds | Speedup | Exact sequence equality |
|---:|---:|---:|---:|---:|---:|---|
| 1,500 | 64 | 0 | 0.0072657000 | 0.0073589000 | 0.9873350622x | PASS |

The benchmark confirms exact equality. At this small synthetic size, Python bookkeeping offset the saved arithmetic, but the implementation now avoids the repeated full retained-set recomputation pattern and preserves the exact candidate rule.

### Issue 4. Coordinate-exchange visitation RNG depended on start-list order

- **Reproduced:** PASS by inspection. The active optimizer passed one advancing RNG through the start list, so warm-start insertion or start order could alter a base start's target-position visitation schedule.
- **Correction implemented:** Each starting assignment receives a deterministic per-start RNG seed from `RANDOM_SEED`, objective type, candidate K, and a `hashlib.blake2b` fingerprint of the assignment vector. Support size and start-list position are excluded.
- **Validation performed:** Same assignment produced the same permutation schedule at B=5,000 and B=40,000; warm-start insertion did not change the base start schedule; unrelated start reordering did not change a start schedule; a fixed seed reproduced the full coordinate-exchange path when objective values and pools were unchanged.
- **Result:** PASS.

Coordinate-exchange reproducibility check:

| Start | Seed | Repeated selected path | Final SBAD |
|---|---:|---|---:|
| `[0, 1, 2]` | 3879319730 | `[0, 1, 4]` both runs | 20.2143383026 |


### Issue 5. Support-resolution confirmation was not a separate expansion

- **Reproduced:** PASS by inspection. `screen_support_resolution()` previously set `confirmation_stage` as soon as the required stable-stage count was reached.
- **Correction implemented:** Added a support-confirmation state machine. Required stable stages now establish provisional stability only. A larger nested support prefix is then evaluated as the separate confirmation stage when available.
- **Validation performed:** Unit validation confirms that stable 10,000 and 20,000 stages force evaluation of 40,000; only the 40,000 row is marked `confirmation_stage=True`; successful confirmation selects 40,000; failed confirmation resets provisional stability; max-size provisional stability reports `stable_at_max_without_separate_confirmation`.
- **Result:** PASS.

### Issue 6. Focused AD-refinement improvement mixed two effects

- **Reproduced:** PASS by inspection. The prior calculation used previous-stage `SBAD_star` and current-stage `SBAD_star`.
- **Correction implemented:** The retained panel is exactly re-evaluated at the current support prefix before focused refinement. `focused_AD_refinement_improvement` is calculated from `pre_refinement_best_SBAD` and `post_refinement_best_SBAD` at the same support prefix.
- **Validation performed:** Unit validation checks 100 to 99 equals 0.01, verifies that a previous-stage value of 95 does not enter the calculation, and verifies no better focused design reports 0.
- **Result:** PASS.

### Issue 7. Development selected-set benchmark ran during normal startup

- **Reproduced:** PASS by inspection. Normal `run_unit_validations()` previously performed 10,000 slow selected-set cKDTree reference queries.
- **Correction implemented:** Added `RUN_DEVELOPMENT_BENCHMARKS = False` and moved the 10,000-evaluation old-versus-new timing benchmark behind that flag. Small exact equality checks still run during normal initialization.
- **Validation performed:** Unit validation records `development_selected_set_benchmark_run = False` during normal initialization, verifies exact equality tests still execute, and probes the development benchmark path with an explicit small enabled run. When the flag is enabled without an override, the configured benchmark length remains 10,000.
- **Result:** PASS.

## Engine cleanup

The initialization cell was refactored so there is exactly one active top-level production definition for every function/class name. Reference implementations use explicit reference-only names, such as `selected_nearest_neighbor_distances_ckdtree_reference` and `candidate_sequence_bruteforce_reference`.

AST structural validation:

- `duplicate_top_level_definition_count = 0`
- `duplicate_top_level_definition_names = []`

## Reduced end-to-end acceptance run

Executed a real reduced run with an irregular projected 850-row two-proxy synthetic survey:

- `N_SAMPLES = 12`
- `N_DESIGN_COMPONENTS = 2`
- `CENTER_REPLICATES = 2`
- `SAMPLE_BUDGET_MODE = "rssd_with_support"`
- `SUPPORT_SITE_MODE = "legacy_inspired_auto"`
- reduced support/K/start limits for acceptance-test runtime only

Run result:

- Stage 10/10 completed: PASS
- End-to-end elapsed time for `run_esap_rssd`: 0.3880822998 seconds
- selected sites: 12
- response-surface sites: 10
- spatial support sites: 2
- final support prefix: 160
- final candidate K: 8
- support-site candidate counts: 112, 112
- support-site SBAD reductions: 6.7370947361, 6.7077856302
- support-site brute-force exact ranking matches: true, true
- figure PNGs generated in the temporary run: 11

Cache diagnostics from the reduced run:

- cache hits: 7,515
- cache misses: 186
- cache evictions: 0
- peak cached vectors: 186
- peak cache MiB: 0.113525390625

Required outputs were written and programmatically verified in the temporary run directory:

- `ESAP_RSSD_selected_sites.csv`
- `ESAP_RSSD_spatial_support_sites.csv`
- `ESAP_RSSD_candidate_saturation.csv`
- `ESAP_RSSD_ad_support_resolution.csv`
- `ESAP_RSSD_optimizer_stability.csv`
- `ESAP_RSSD_run_summary.md`


## Final targeted correction validation

Additional pre-field-run unit validations now cover:

| Test | Result | Evidence / note |
|---|---|---|
| Stable 10,000 and 20,000 support stages evaluate 40,000 before stopping. | PASS | `support_confirmation_state_machine_preview()` returned rows through 40,000. |
| `confirmation_stage=True` appears only on the separate confirmation row when confirmation succeeds. | PASS | 10,000 and 20,000 were stable stages only; 40,000 was the confirmation stage. |
| Unstable confirmation resets provisional stability. | PASS | A failed 40,000 confirmation returned `confirmation_failed_reset`, and the next prefix was not marked as confirmation. |
| Final support size equals the confirmation prefix when confirmation succeeds. | PASS | Successful confirmation selected 40,000. |
| Stable-at-maximum without a separate confirmation is reported explicitly. | PASS | The status is `stable_at_max_without_separate_confirmation`; the row is not marked as confirmation. |
| Focused refinement 100 to 99 reports 0.01. | PASS | `focused_ad_refinement_improvement(100, 99) == 0.01`. |
| Previous-stage SBAD does not enter focused improvement. | PASS | With previous-stage 95, pre-refinement 100, post-refinement 99, focused improvement remains 0.01. |
| No better focused refinement reports 0. | PASS | `focused_ad_refinement_improvement(100, 100.5) == 0`. |
| Normal initialization skips the 10,000-query development benchmark. | PASS | `development_selected_set_benchmark_run = False` by default. |
| Exact equality validations still execute during normal initialization. | PASS | Randomized selected sets compare vectorized distances to brute force and geoMSD to the cKDTree reference. |
| Development benchmark path still runs when explicitly enabled. | PASS | Unit validation probes the enabled path with a small explicit run; the default enabled length remains 10,000. |
| Support screening does not run full final optimizer phases at every support stage. | PASS | Source validation confirms `screen_support_resolution()` uses `optimization_phase="support_screen"` and not `optimization_phase="final"`. |

## Acceptance-test matrix

| # | Test | Result | Evidence / note |
|---:|---|---|---|
| 1 | `SUPPORT_GAP_ANCHORS` exists in `RSSDConfig`. | PASS | Field added with default 500. |
| 2 | `SUPPORT_CANDIDATE_NEIGHBORS_PER_ANCHOR` exists in `RSSDConfig`. | PASS | Field added with default 5. |
| 3 | Both fields are validated as positive integers. | PASS | `validate_config` rejects values below 1. |
| 4 | `add_spatial_support_sites()` executes in a real end-to-end run. | PASS | 850-row run completed Stage 9 and Stage 10. |
| 5 | At least one bounded support candidate is evaluated. | PASS | Candidate counts were 112 and 112. |
| 6 | Exact support-site candidate ranking matches brute force over the same bounded candidate set. | PASS | Both support additions matched brute-force exact SBAD ranking. |
| 7 | Support-site addition does not increase SBAD. | PASS | Reductions were 6.7370947361 and 6.7077856302. |
| 8 | Support-site target fields export as null. | PASS | Theoretical target IDs, target PCs, replicate number, and PCA distance were null; `target_type` was `support`. |
| 9 | Vectorized nearest-selected-site distances match scipy brute force. | PASS | Sizes 6, 10, 12, 20, and 40 tested. |
| 10 | Vectorized geoMSD matches the previous cKDTree implementation. | PASS | Strict equality test passed. |
| 11 | Vectorized minimum separation matches brute force. | PASS | Randomized selected-set tests passed. |
| 12 | Statistical values are unchanged on randomized selected sets. | PASS | Randomized tests across requested sizes passed. |
| 13 | Normal initialization skips the 10,000-evaluation development benchmark. | PASS | `development_selected_set_benchmark_run = False`; historical timing remains development evidence. |
| 14 | Vectorized method is used in production geoMSD calculation. | PASS | `exact_geo_msd` calls vectorized nearest-selected distances. |
| 15 | No repeated `workers=-1` selected-site cKDTree query remains in the production objective path. | PASS | The old selected-set cKDTree function is reference-only. |
| 16 | Incremental `min_geo` sequence matches brute force at one PCA tolerance. | PASS | Complete sequence equality passed. |
| 17 | Incremental sequence matches progressive-shell brute force when PCA tolerance expands. | PASS | Progressive-shell sequence equality passed. |
| 18 | Candidate prefixes are literally nested. | PASS | Prefix identity checked at K=3, 6, 12, and 24 when available. |
| 19 | Previously retained candidates survive tolerance expansion. | PASS | Progressive-shell retained prefixes remained unchanged. |
| 20 | Candidate tie-breaking remains geographic distance, PCA distance, then stable index. | PASS | Incremental and brute-force reference sequences matched exactly. |
| 21 | Large synthetic candidate benchmark is completed. | PASS | 1,500-neighborhood, Kmax 64 benchmark completed. |
| 22 | Exact candidate-sequence equality is reported. | PASS | Equality was true. |
| 23 | Support size is absent from per-start visitation seed construction. | PASS | Seed uses random seed, objective, K, and assignment fingerprint only. |
| 24 | Start-list position is absent from visitation seed construction. | PASS | Same assignment preview is independent of list context. |
| 25 | Stable assignment fingerprint uses a deterministic hashing method. | PASS | Uses `hashlib.blake2b`. |
| 26 | Python built-in `hash()` is not used for assignment fingerprinting. | PASS | Source uses no built-in `hash()` for this purpose. |
| 27 | Same assignment has same permutation schedule at B=5,000 and B=40,000. | PASS | Per-start preview schedules matched. |
| 28 | Warm-start insertion does not change a base start's permutation schedule. | PASS | Base schedule check passed after warm-start insertion. |
| 29 | Reordering unrelated starts does not change a start's permutation schedule. | PASS | Per-start seed depends only on assignment fingerprint, not list order; validation preview passed. |
| 30 | Fixed `RANDOM_SEED` reproduces the same path when objective values are unchanged. | PASS | Coordinate-exchange path repeated with same selected result and SBAD. |
| 31 | Exactly one production `RSSDConfig` definition exists. | PASS | AST count is 1. |
| 32 | Exactly one production `SupportDistanceCache` definition exists. | PASS | AST count is 1. |
| 33 | Exactly one production `SBADNearestState` definition exists. | PASS | AST count is 1. |
| 34 | Exactly one production `OptimizationStartBank` definition exists. | PASS | AST count is 1. |
| 35 | Exactly one production `build_nested_candidate_sequences` definition exists. | PASS | AST count is 1. |
| 36 | Exactly one production `screen_candidate_saturation` definition exists. | PASS | AST count is 1. |
| 37 | Exactly one production `screen_support_resolution` definition exists. | PASS | AST count is 1. |
| 38 | Exactly one production `coordinate_exchange_sbad` definition exists. | PASS | AST count is 1. |
| 39 | Exactly one production `optimize_multiple_starts_sbad` definition exists. | PASS | AST count is 1. |
| 40 | Exactly one production `add_spatial_support_sites` definition exists. | PASS | AST count is 1. |
| 41 | Exactly one production `proxy_spacing_diagnostic` definition exists. | PASS | AST count is 1. |
| 42 | Exactly one production `run_esap_rssd` definition exists. | PASS | AST count is 1. |
| 43 | Exactly one production `run_unit_validations` definition exists. | PASS | AST count is 1. |
| 44 | AST duplicate top-level definition count equals zero. | PASS | Duplicate count was 0. |
| 45 | Reference implementations have explicit reference or test-only names. | PASS | Reference names include `*_reference`. |
| 46 | Notebook parses as valid Jupyter JSON. | PASS | Parsed with `json.loads`. |
| 47 | Every code cell passes syntax parsing. | PASS | All code cells passed `ast.parse`. |
| 48 | Engine initialization completes. | PASS | Engine cell executed. |
| 49 | Unit validations complete. | PASS | Unit validations completed. |
| 50 | An irregular synthetic survey with at least 800 rows is generated. | PASS | Generated 850 irregular projected rows. |
| 51 | Two correlated spatial sensor predictors are used. | PASS | Used `sensor_a` and `sensor_b`. |
| 52 | `N_SAMPLES = 12`. | PASS | End-to-end config used 12. |
| 53 | `N_DESIGN_COMPONENTS = 2`. | PASS | End-to-end config used 2. |
| 54 | `rssd_with_support` is used. | PASS | End-to-end config used `rssd_with_support`. |
| 55 | Final selected-site count equals 12. | PASS | Selected count was 12. |
| 56 | Response-surface count equals 10. | PASS | Response-surface count was 10. |
| 57 | Spatial-support count equals 2. | PASS | Spatial-support count was 2. |
| 58 | Final coordinates are unique. | PASS | Unique-coordinate assertion passed. |
| 59 | Hybrid core satisfies `SBAD <= SBAD_limit`. | PASS | Reduced run satisfied the envelope. |
| 60 | Both support additions have nonnegative SBAD reduction. | PASS | Both reductions were positive. |
| 61 | Candidate-saturation output contains objective metrics. | PASS | Required metric columns were present. |
| 62 | Cache diagnostics are present. | PASS | Hits, misses, evictions, and peak MiB were present. |
| 63 | No `AttributeError` occurs. | PASS | End-to-end run completed without exception. |
| 64 | Stage 10/10 completes. | PASS | Stage 10 printed and run completed. |
| 65 | Required CSV and Markdown outputs are written. | PASS | Required files were verified in the run directory. |
| 66 | Standardized retained PCs remain approximately zero mean. | PASS | Unit PCA validation passed. |
| 67 | Standardized retained PCs remain approximately unit sample SD. | PASS | Unit PCA validation passed. |
| 68 | Retained PCs remain approximately decorrelated. | PASS | Unit PCA correlation validation passed. |
| 69 | PCA target membership is never violated. | PASS | Each response-surface target instance had exactly one selected response-surface site. |
| 70 | Selected sites remain unique. | PASS | Assignment and final coordinate uniqueness assertions passed. |
| 71 | SBAD remains exact for the fixed support prefix. | PASS | Direct SBAD and cached prefix SBAD tests passed. |
| 72 | SBAD coverage envelope remains unchanged. | PASS | Formula remains `(1 + AD_COVERAGE_ENVELOPE_REL_TOL) * SBAD_star`. |
| 73 | Exact geoMSD definition remains unchanged. | PASS | Vectorized implementation matched cKDTree and brute force. |
| 74 | Minimum-separation tie-break remains. | PASS | Hybrid and support-site ranking still use minimum separation as tie-breaker. |
| 75 | No weighted SBAD/geoMSD score exists. | PASS | Source and objective logic remain lexicographic. |
| 76 | No Moran predictor objective exists. | PASS | No Moran objective is implemented. |
| 77 | No survey-wide N by N distance matrix exists. | PASS | Only small selected-set and bounded/reference arrays are used. |
| 78 | No Cartesian product of candidate pools exists. | PASS | Assignment uses candidate-pool cost matrices, not pool products. |
| 79 | No raster topology assumption is introduced. | PASS | Spatial logic uses projected coordinates and cKDTree searches. |
| 80 | Spatial support sites remain sequential SBAD-reducing additions. | PASS | End-to-end support-site reductions were positive. |
| 81 | Regression diagnostics use all final calibration sites. | PASS | `selected_scores` for all final sites are passed to regression diagnostics. |
| 82 | Methods describes the corrected final v2.10 code. | PASS | Methods file updated in place. |
| 83 | Changelog documents these as v2.10 pre-field-run corrections. | PASS | Changelog section added. |
| 84 | Implementation report distinguishes historical development benchmarks from normal startup validation. | PASS | Historical timing is reported above; normal startup skip is validated. |
| 85 | Every acceptance test is marked PASS, FAIL, or PARTIAL. | PASS | This matrix marks all 87 items. |
| 86 | No unexecuted validation is described as PASS. | PASS | PASS items are based on executed tests or explicit structural/source validation. |
| 87 | No placeholder cells or pseudocode remain. | PASS | Notebook JSON and every code cell parse; engine executed successfully. |

## Remaining notes

The reduced acceptance run intentionally used smaller support, candidate-K, and optimizer-start limits for runtime. These limits do not change SBAD, the SBAD envelope definition, exact geoMSD, coordinate-exchange ranking, or spatial support-site ranking. They should not be copied as scientific defaults for the full 2.3-million-row field run.
