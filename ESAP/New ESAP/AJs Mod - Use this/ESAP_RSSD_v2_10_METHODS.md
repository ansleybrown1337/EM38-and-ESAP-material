# ESAP RSSD v2.10 Methods

## Scope

ESAP RSSD v2.10 is a targeted implementation correction and efficiency revision to the v2.9 statistical design. It does not redefine the sampling method.

The implementation preserves:

- standardized PC response-surface design;
- Spatially Balanced Average Distance (SBAD);
- nested spatially balanced geographic support;
- internal SBAD-reference optimization;
- the 5 percent SBAD coverage envelope;
- exact geoMSD maximization inside the coverage envelope;
- minimum-separation tie breaking;
- adaptive candidate-space saturation;
- adaptive SBAD support resolution;
- adaptive optimizer initialization stability;
- sequential exact SBAD-reducing spatial support-site allocation;
- proxy spatial-scale diagnostics.

Key principles:

> ESAP 2 separates geographic support from sensor observation density.

> Adaptive diagnostics should vary one source of uncertainty at a time.

## Response-Surface Statistics

User-selected sensor variables are transformed only when explicitly configured, centered and scaled, then passed through PCA. Retained design-PC scores are divided by the square root of the fitted PCA explained variance so retained PCs are approximately zero mean, unit sample SD, and decorrelated.

Response-surface targets are built in this standardized retained-PC space. The design radius is the configured empirical quantile of retained-PC radial distances. The full one- through four-PC CCD remains available, with cube points, axial points, and configurable center replicates. PCA-space chi-square outliers are excluded from response-surface candidate selection but are not silently deleted from the source table.

## SBAD and Hybrid Objective

SBAD is:

```text
SBAD(S) = mean_b min_s ||u_b - s||
```

where `u_b` are nested spatially balanced geographic support coordinates and `s` are selected calibration coordinates. For a fixed support prefix, SBAD is exact.

The AD-reference design minimizes exact SBAD subject to PCA target membership and site uniqueness. The hybrid response-surface core then uses:

```text
SBAD_limit = (1 + AD_COVERAGE_ENVELOPE_REL_TOL) * SBAD_star
```

The hybrid objective keeps PCA target membership as a hard constraint, requires SBAD inside the envelope, maximizes exact Lesch Eq. 9 geoMSD, then tie-breaks by absolute minimum selected-site separation, mean PCA target distance, and maximum PCA target distance.

No weighted SBAD/geoMSD score, Moran predictor objective, boundary penalty, raster topology, or required downstream spatial regression model is introduced.

## Selected-Set Distance Calculation

geoMSD and minimum separation are calculated from an exact vectorized `m` by `m` Euclidean distance array on the small selected calibration set:

```text
d_j = min_{k != j} ||s_j - s_k||
geoMSD = exp(mean(log(d_j)))
```

The selected-set distance array scales with the calibration sample budget `m`, not the survey population `N`. It is not a survey-wide pairwise distance matrix.

For ordinary RSSD sample sizes, `m` is usually about 6 to 40. For `m = 20`, the direct array contains 400 entries. v2.10 uses this exact vectorized calculation in the production geoMSD and minimum-separation path to avoid repeated threaded cKDTree setup for tiny selected sets during coordinate exchange. cKDTree remains used for large or appropriate search problems, including PC-space neighborhoods, support-to-selected SBAD queries, geographic support-site candidate queries, and existing-location matching.

## Shared Exact Support-Distance Cache

v2.10 uses a shared `SupportDistanceCache` built for the maximum nested support prefix needed by the run. For a candidate `c`, the cached vector is the exact Euclidean distance from every maximum-support coordinate to `c`. Smaller support stages use exact vector prefixes.

The cache is bounded by `AD_DISTANCE_CACHE_MAX_MIB`. Stored vectors are `float32` for memory efficiency; SBAD means, envelope comparisons, and objective comparisons use `float64`.

Caching and prefix slicing change computational reuse only. They do not approximate SBAD.

## Candidate Sequences and Incremental `min_geo`

v2.10 builds one candidate sequence per unique base PCA target. Replicated target instances reference the same sequence.

The candidate-selection rule is unchanged:

1. choose the observation with minimum PCA target distance first;
2. then greedily choose observations that maximize geographic distance from the retained candidate set;
3. tie-break by smaller PCA target distance;
4. tie-break by stable analysis index.

The corrected implementation maintains a running vector:

```text
min_geo_i = minimum distance from available observation i to the retained candidate set
```

After a new candidate `c` is retained:

```text
min_geo_i = min(min_geo_i, distance(i, c))
```

Only distances to the newly retained candidate are computed for already available observations. This preserves the exact farthest-point sequence while avoiding repeated recomputation of distances from every remaining observation to every retained candidate.

## PCA Tolerance Expansion

Candidate prefixes remain literally nested when PCA tolerance expands. Previously retained candidates are never removed. When a wider PCA-tolerance shell adds newly eligible observations, those new observations are initialized with their exact minimum geographic distance to the complete retained set. Existing available observations keep their current `min_geo` values.

Therefore, when enough candidates exist:

```text
C3 subset C6 subset C12 subset C24 subset C48
```

is a literal prefix relationship, not just a set-size statement.

Candidate sequence records include:

- `candidate_sequence_rank`;
- `candidate_added_at_tolerance`;
- `candidate_tolerance_expansion_stage`.

## Support-Resolution Stability

v2.10 removes exact site-set identity as the primary support-resolution stability criterion. A swap among practically tied designs does not automatically mean the coverage objective is unstable.

Support-resolution screening evaluates:

- relative change in best AD-reference SBAD across support prefixes;
- practical-equivalence pair counts;
- decisive pair order agreement;
- near-best set overlap;
- focused AD-refinement improvement at the current support prefix;
- hybrid SBAD;
- coverage ratio;
- exact geoMSD;
- minimum selected-site separation.

The support-resolution diagnostic now separates provisional stability from confirmation. A support stage with acceptable practical-equivalence metrics is a `stable_stage`. After `AD_SUPPORT_STABLE_STAGES_REQUIRED` consecutive stable stages, v2.10 does not immediately declare support resolution confirmed. If a larger nested support prefix is available, the next larger prefix is evaluated as a separate `confirmation_stage`.

At that confirmation prefix, the retained design panel is first re-evaluated exactly, then the normal focused warm-start refinement is run. The same practical-equivalence-aware support-stability gate is applied again. If the confirmation stage is stable, `ad_support_resolution_stable = True` and the final support size is the confirmation prefix. If it is not stable, provisional stability is reset and support expansion continues when possible.

If the maximum configured support size is reached after the required consecutive stable stages but no larger prefix exists for a separate confirmation expansion, the run reports `stable_at_max_without_separate_confirmation`. The last stable stage is not silently labeled as a confirmation stage.

The support-resolution CSV distinguishes:

- `stable_stage`;
- `confirmation_stage`;
- `support_resolution_status`;
- `pre_refinement_best_SBAD`;
- `post_refinement_best_SBAD`;
- `focused_AD_refinement_improvement`.

## Focused AD-Reference Refinement Diagnostic

At an expanded support prefix `B_current`, v2.10 separates support-resolution change from optimizer refinement at that fixed prefix.

Before focused refinement, the retained design panel from the previous support stage is evaluated exactly under `B_current`. The best of those values is:

```text
pre_refinement_best_SBAD
```

Focused coordinate-exchange refinement then starts from the best re-evaluated panel designs. The best AD-reference SBAD after that focused refinement is:

```text
post_refinement_best_SBAD
```

The focused-refinement diagnostic is:

```text
focused_AD_refinement_improvement =
max(0, (pre_refinement_best_SBAD - post_refinement_best_SBAD)
       / max(abs(pre_refinement_best_SBAD), numerical_epsilon))
```

This answers whether optimization at the fixed support prefix found a materially better coverage design than was already represented in the retained panel. It is distinct from:

```text
relative_change_in_best_AD_reference_SBAD
```

which describes how the best AD-reference SBAD changes across different geographic support prefixes.

Screening uses moderate starts and warm-start refinement. One full final AD-reference optimization and one full final hybrid optimization are run after support size and candidate K are finalized.

## Per-Start Reproducible Coordinate Exchange

Random candidate-position visitation during coordinate exchange is now reproducible per starting assignment. Each start receives its own deterministic RNG seed based on:

- `RANDOM_SEED`;
- objective type;
- candidate K;
- a stable cryptographic fingerprint of the starting assignment.

The fingerprint uses deterministic bytes from the selected analysis-index vector and `hashlib.blake2b`. Python built-in `hash()` is not used.

The per-start visitation seed does not include support size, the start's position in the current list, the number of warm starts, or the number of earlier starts. Thus, support-resolution comparisons hold both the base start schedule and the coordinate-exchange visitation schedule constant for a fixed starting assignment. Observed changes are attributable to the geographic support criterion rather than unrelated random initialization changes.

## Batched Optimizer Initialization Stability

Starts run in batches. The optimizer records:

- batch number;
- starts in batch;
- cumulative starts;
- best SBAD;
- best geoMSD;
- best minimum separation;
- relative best-objective improvement;
- recent near-best fraction;
- stable-batch flag;
- initialization-stable flag;
- stop reason.

Coordinate-exchange convergence remains separate from initialization stability.

## Spatial Support Sites

Spatial support sites are selected after the final response-surface core is optimized. They are sequential exact SBAD-reducing additions. Exported spatial support rows use `sample_role = "spatial_support"` and `target_type = "support"`; theoretical target IDs, target PC coordinates, target replicate number, and PCA target distance remain null.

The support-site pathway uses:

- `SUPPORT_GAP_ANCHORS`: number of most poorly covered geographic support locations used to identify possible support-site regions. Recommended default: 500. Increase only for unusually large or fragmented survey domains when support-site candidate search appears too geographically restricted.
- `SUPPORT_CANDIDATE_NEIGHBORS_PER_ANCHOR`: number of nearby candidate-eligible survey observations retrieved around each high-gap support location. Recommended default: 5. Increase when sensor observations are sparse or irregular and the bounded support-site candidate set is too small.

For each support-site addition, v2.10 identifies high-gap support anchors, queries nearby candidate-eligible observations, deduplicates the bounded candidate set, evaluates exact final SBAD for every bounded candidate, and tie-breaks by minimum separation and stable index.

## Proxy Spatial-Scale Diagnostic

The proxy spatial-scale diagnostic is diagnostic only. It never changes the hybrid optimizer.

v2.10 requires adequate pair counts per interpreted lag bin, consecutive threshold attainment, rolling-median smoothing for plateau detection, final-tail slope checks, and oscillatory-tail failure checks. Unreliable proxy ranges are reported as unreliable.

## Development Benchmarks

`RUN_DEVELOPMENT_BENCHMARKS = False` during normal engine initialization. Startup validations still run small exact equality checks for selected-site nearest-neighbor distances, geoMSD, and minimum separation, including cKDTree reference comparisons on randomized selected sets.

The 10,000-evaluation old-cKDTree-versus-new-vectorized timing benchmark is retained as an opt-in development benchmark. It is not run during normal field startup. When explicitly enabled, the benchmark records timing results and equality status.

## Validation Requirement

The completed v2.10 implementation was validated with a reduced irregular two-proxy end-to-end run before being considered ready for a full field-data run. That run used at least 800 irregular projected observations, `N_SAMPLES = 12`, `N_DESIGN_COMPONENTS = 2`, `rssd_with_support`, and legacy-inspired automatic support allocation. It completed Stage 10/10 with 10 response-surface sites and 2 spatial support sites.

The validation also executed selected-set distance equality tests, support-confirmation state-machine tests, true focused-refinement calculation tests, development-benchmark flag tests, incremental candidate-sequence equality tests, candidate-sequence timing, per-start RNG reproducibility tests, support-site brute-force ranking checks, and AST duplicate-definition validation. The historical 10,000-evaluation selected-set timing benchmark remains documented as development evidence, but it is not part of normal field engine initialization.
