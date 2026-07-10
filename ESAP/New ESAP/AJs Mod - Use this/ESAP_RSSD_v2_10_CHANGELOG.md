# ESAP RSSD v2.10 changelog

This changelog compares `ESAP_RSSD_v2_9_scalable.ipynb` with `ESAP_RSSD_v2_10_scalable.ipynb`. v2.10 is a targeted implementation correction and efficiency revision; it preserves the v2.9 statistical architecture.

## Pre-field-run v2.10 implementation corrections

These corrections were completed during v2.10 development before the first full field-data run. They are not a v2.10 to v2.10.1 change.

### 1. Missing support-site configuration fields added

**Old implementation behavior:** `add_spatial_support_sites()` referenced `SUPPORT_GAP_ANCHORS` and `SUPPORT_CANDIDATE_NEIGHBORS_PER_ANCHOR`, but the fields were not present in `RSSDConfig`.

**Problem:** A normal `rssd_with_support` run could fail at Stage 9 with an `AttributeError`.

**Corrected v2.10 behavior:** Both fields are now defined, validated as positive integers, exposed in advanced settings, and documented.

**Statistical or computational rationale:** The bounded exact support-site search needs explicit, auditable controls without changing the SBAD objective.

### 2. Support-site pathway executed in acceptance testing

**Old implementation behavior:** Earlier reduced validation did not fully exercise the spatial support-site pathway.

**Problem:** A missing support-site configuration field was not caught before runtime.

**Corrected v2.10 behavior:** The reduced end-to-end acceptance run uses `N_SAMPLES = 12`, `rssd_with_support`, and legacy-inspired automatic support allocation, producing 10 response-surface sites and 2 spatial support sites.

**Statistical or computational rationale:** Support-site validation must execute the actual sequential exact SBAD-reduction pathway.

### 3. Tiny selected-set cKDTree calls replaced

**Old implementation behavior:** `selected_nearest_neighbor_distances()` built a cKDTree and called `query(..., k=2, workers=-1)` for each small selected set.

**Problem:** Coordinate exchange evaluates geoMSD and minimum separation many times on selected sets of about 6 to 40 sites; threaded tree setup dominated runtime.

**Corrected v2.10 behavior:** Production geoMSD and minimum-separation calculations use an exact vectorized `m` by `m` selected-site Euclidean distance array.

**Statistical or computational rationale:** The calculation is exact and preserves Lesch Eq. 9 while avoiding repeated tiny-tree overhead.

### 4. Selected-set array distinguished from prohibited survey matrix

**Old implementation behavior:** The distinction was not explicit enough in documentation.

**Problem:** A direct selected-set distance array could be confused with a prohibited survey-wide `N` by `N` matrix.

**Corrected v2.10 behavior:** Methods now state that the selected-set array scales with calibration sample count `m`, not survey population `N`.

**Statistical or computational rationale:** Exact small selected-set distances are appropriate; survey-wide pairwise matrices remain prohibited.

### 5. Candidate farthest-point sequence made incremental

**Old implementation behavior:** Candidate sequence construction recomputed distances from every remaining observation to every retained candidate at each greedy step.

**Problem:** That repeated exact calculation was redundant.

**Corrected v2.10 behavior:** The implementation maintains an exact running `min_geo` vector and updates it only with distances to the newly retained candidate.

**Statistical or computational rationale:** The candidate-selection rule is unchanged, but exact redundant work is removed.

### 6. Progressive tolerance shells preserve nesting

**Old implementation behavior:** Tolerance expansion was intended to be nested but the active implementation still rebuilt full remaining-to-retained distances each step.

**Problem:** Prefix identity after tolerance expansion needed explicit validation.

**Corrected v2.10 behavior:** Previously retained candidates are preserved; newly eligible shell observations are initialized against the retained set; existing `min_geo` values are retained.

**Statistical or computational rationale:** K-stage comparisons now add alternatives without reshuffling earlier prefixes.

### 7. Coordinate-exchange visitation RNG made per-start

**Old implementation behavior:** One advancing RNG was shared across starts in `optimize_multiple_starts_sbad()`.

**Problem:** Warm-start insertion or start-list ordering could change the visitation schedule for an otherwise identical base start.

**Corrected v2.10 behavior:** Each starting assignment receives a deterministic per-start RNG.

**Statistical or computational rationale:** Adaptive diagnostics should vary one source of uncertainty at a time.

### 8. Starting-assignment fingerprinting made stable

**Old implementation behavior:** The base start bank was support-size independent, but coordinate-exchange visitation still depended on start sequence position.

**Problem:** Support-resolution comparisons could still be partly confounded by unrelated RNG advancement.

**Corrected v2.10 behavior:** Per-start seeds use `RANDOM_SEED`, objective type, candidate K, and a `hashlib.blake2b` fingerprint of the starting analysis-index vector. Python built-in `hash()` is not used.

**Statistical or computational rationale:** Fixed starts receive fixed visitation schedules across support sizes, warm-start insertion, and unrelated start reordering.

### 9. Duplicate superseded engine definitions removed

**Old implementation behavior:** The engine cell contained multiple historical and override definitions with repeated names.

**Problem:** Python used the last definition, but code inspection was ambiguous.

**Corrected v2.10 behavior:** The initialization cell now has one top-level production definition for each function/class name.

**Statistical or computational rationale:** A single canonical implementation reduces audit risk before a large field-data run.

### 10. AST duplicate-definition validation added

**Old implementation behavior:** Duplicate-definition cleanup was not validated programmatically.

**Problem:** Manual inspection could miss repeated top-level names.

**Corrected v2.10 behavior:** The engine is parsed with `ast`, top-level function/class names are counted, and duplicate count is reported.

**Statistical or computational rationale:** The structural test makes the implementation state auditable.

### 11. Reduced irregular end-to-end acceptance run added

**Old implementation behavior:** Prior validation used a smaller smoke run and did not cover every support-site assertion.

**Problem:** Full-field execution should not be attempted until a reduced irregular dataset reaches Stage 10/10.

**Corrected v2.10 behavior:** An 850-row irregular two-proxy run completed Stage 10/10, wrote required outputs, produced 10 response-surface sites and 2 spatial support sites, and verified brute-force exact support-site ranking over emitted bounded candidate sets.

**Statistical or computational rationale:** The reduced run exercises the actual final architecture without weakening SBAD, the coverage envelope, geoMSD, candidate saturation, support resolution, or support-site selection.

### 12. Support-resolution confirmation made separate from provisional stability

**Old implementation behavior:** `screen_support_resolution()` set `confirmation_stage = stable_count >= AD_SUPPORT_STABLE_STAGES_REQUIRED` and stopped immediately.

**Problem:** The last provisional stable stage was labeled as confirmation, so an additional nested support prefix was not evaluated when one was available.

**Corrected v2.10 behavior:** After the required consecutive stable support stages, v2.10 evaluates one additional larger support prefix as the confirmation stage. `stable_stage` and `confirmation_stage` are separate CSV fields, and `stable_at_max_without_separate_confirmation` is reported when no larger prefix exists.

**Statistical or computational rationale:** Support-resolution confirmation must test stability after one more increase in geographic support, not merely count the provisional stages.

### 13. Focused AD-refinement improvement corrected

**Old implementation behavior:** Focused improvement was calculated from previous-stage `SBAD_star` and current-stage `SBAD_star`.

**Problem:** That mixed support-resolution change with optimizer refinement and did not answer whether focused refinement at the current support prefix found a materially better design.

**Corrected v2.10 behavior:** The retained panel is exactly re-evaluated at the current support prefix before refinement. `focused_AD_refinement_improvement` is calculated from `pre_refinement_best_SBAD` and `post_refinement_best_SBAD` at the same prefix.

**Statistical or computational rationale:** The support-stability gate now separates geographic support change from optimization improvement at a fixed support resolution.

### 14. Development selected-set timing benchmark removed from normal initialization

**Old implementation behavior:** `run_unit_validations()` ran 10,000 calls to the deliberately slow selected-set cKDTree reference path during every engine initialization.

**Problem:** That timing benchmark is useful development evidence but can add substantial startup time before field runs.

**Corrected v2.10 behavior:** Normal initialization runs small exact equality validations only. The 10,000-evaluation timing benchmark is controlled by `RUN_DEVELOPMENT_BENCHMARKS` and is skipped by default while recording `development_selected_set_benchmark_run = False`.

**Statistical or computational rationale:** Startup validation should verify correctness without repeatedly running a development performance benchmark.

## 1. Support-size-dependent optimizer seeds removed

**Old behavior:** Optimizer random starts could vary with SBAD support size.

**Problem:** Support-resolution diagnostics mixed two sources of variation: geographic support resolution and random initialization.

**New behavior:** Start schedules are seeded by `RANDOM_SEED`, objective type, and candidate K, not support size.

**Statistical or computational rationale:** Support-resolution comparisons should isolate support resolution.

## 2. Reusable optimization start banks added

**Old behavior:** Starts were generated inside each optimization stage.

**Problem:** Repeated generation made it difficult to guarantee identical base start schedules across support prefixes.

**New behavior:** `OptimizationStartBank` builds a reusable base sequence and allows warm starts without mutating that base sequence.

**Statistical or computational rationale:** Identical candidate pools and seed now produce the same base start sequence across support sizes.

## 3. Exact site-set identity removed as a support-stability requirement

**Old behavior:** Exact selected-site identity was treated as a major stability signal.

**Problem:** Nearly tied designs can exchange one site without materially changing SBAD or the hybrid objective.

**New behavior:** Site-set overlap is reported diagnostically, but it is not the primary stability gate.

**Statistical or computational rationale:** Objective stability matters more than exact identity among practically equivalent designs.

## 4. Raw Spearman criterion replaced

**Old behavior:** v2.9 used a raw rank-correlation style stability test.

**Problem:** A high global rank correlation can hide important near-best changes, while low correlation among tied designs can overstate instability.

**New behavior:** v2.10 uses practical-equivalence-aware stability with decisive pair agreement and near-best set overlap.

**Statistical or computational rationale:** The diagnostic now focuses on decisions that could change the field plan materially.

## 5. Decisive pair order agreement added

**Old behavior:** Pair order changes were not separated from near ties.

**Problem:** Reordering tied designs should not have the same meaning as reversing clearly different designs.

**New behavior:** Pair order is checked only when both compared designs differ beyond the practical-equivalence tolerance.

**Statistical or computational rationale:** Decisive pair agreement measures ranking stability where ranking is meaningful.

## 6. Near-best set overlap added

**Old behavior:** Stability was summarized without explicitly comparing the near-best design set.

**Problem:** A support prefix can preserve the winner but change the set of practically competitive alternatives.

**New behavior:** The support-resolution CSV reports previous/current near-best set sizes, overlap, and Jaccard similarity.

**Statistical or computational rationale:** The near-best set is the relevant uncertainty set for practical field decisions.

## 7. Full optimization at every support B replaced

**Old behavior:** Full AD-reference and hybrid multiple-start optimization could be rerun independently at every support prefix.

**Problem:** That repeated exact work was expensive and changed initialization schedules.

**New behavior:** v2.10 screens support prefixes with moderate starts, uses focused warm-start refinement, then performs one full final AD-reference and one full final hybrid optimization.

**Statistical or computational rationale:** The final field plan still receives the full objective treatment, while screening avoids redundant work.

## 8. Support-distance cache lifetime extended

**Old behavior:** Exact support-distance calculations were recomputed in multiple stages.

**Problem:** The same candidate/support distance vectors were needed repeatedly by starts, stages, objectives, and support-site addition.

**New behavior:** One bounded shared maximum-support cache is reused across starts and stages.

**Statistical or computational rationale:** Reuse changes only computation, not the exact SBAD quantities.

## 9. Candidate sequences built once per base target

**Old behavior:** Candidate neighborhoods could be regenerated by stage.

**Problem:** Regeneration risks accidental non-nesting and repeated work, especially for replicated targets.

**New behavior:** v2.10 builds one progressive sequence per unique base target and shares it across replicated target instances.

**Statistical or computational rationale:** Replicated theoretical targets should reference the same ordered candidate alternatives.

## 10. Tolerance-shell expansion made truly nested

**Old behavior:** Candidate tolerance expansion could be documented as nested without explicit prefix preservation.

**Problem:** If retained candidates can disappear after tolerance expansion, K-stage comparisons are not literal prefix comparisons.

**New behavior:** Previously retained candidates stay in sequence order; wider tolerance shells append additional candidates.

**Statistical or computational rationale:** Objective changes from K expansion should reflect added alternatives, not reshuffled earlier choices.

## 11. Objective-based candidate saturation added

**Old behavior:** Candidate saturation was closely tied to unique-candidate availability and assignment feasibility.

**Problem:** More available candidates do not necessarily improve SBAD_star, hybrid geoMSD, or minimum separation; conversely, assignment feasibility alone is not a design-quality criterion.

**New behavior:** Candidate K screening records SBAD_star, hybrid SBAD, coverage ratio, exact geoMSD, minimum separation, and PCA mismatch, then applies configured material-change tolerances.

**Statistical or computational rationale:** Candidate saturation should answer whether the attainable design objective has stopped changing materially.

## 12. Final-B candidate confirmation added

**Old behavior:** Candidate K selected at the screening support prefix could be carried into the final design.

**Problem:** A candidate space that appears saturated at a coarse prefix may not be saturated at final support resolution.

**New behavior:** v2.10 reconfirms K at final B and resumes K expansion if material objective improvement appears.

**Statistical or computational rationale:** Final candidate adequacy must be checked at the final exact coverage objective.

## 13. No-improvement patience replaced

**Old behavior:** Optimizer stopping relied on no-improvement patience.

**Problem:** No-improvement patience is not a direct initialization-stability diagnostic.

**New behavior:** Starts run in batches with relative best-objective improvement, recent near-best fraction, stable-batch count, and explicit stop reason.

**Statistical or computational rationale:** Initialization stability should measure whether additional starts are still finding materially different solutions.

## 14. Support-site selection changed to bounded exact ranking

**Old behavior:** Spatial support-site addition used the first unused neighbor near a high-gap support point.

**Problem:** The first unused neighbor is not guaranteed to be the best exact SBAD reducer among nearby candidates.

**New behavior:** v2.10 builds a bounded gap-derived candidate set, deduplicates it, evaluates exact final SBAD for every bounded candidate, and tie-breaks by minimum separation.

**Statistical or computational rationale:** Sequential support sites should reduce the same exact SBAD criterion used by the design.

## 15. Proxy range reliability strengthened

**Old behavior:** Proxy spatial-scale interpretation was less strict about bin support and plateau behavior.

**Problem:** Sparse bins, one-bin threshold crossing, rising tails, or oscillatory tails can produce unreliable proxy ranges.

**New behavior:** v2.10 requires minimum pair counts, consecutive threshold bins, rolling-median plateau detection, final-tail slope checks, and oscillatory-tail flags.

**Statistical or computational rationale:** The proxy diagnostic should report uncertainty rather than overinterpret predictor structure.

## 16. Run-summary candidate warning improved

**Old behavior:** Candidate status was less explicit in the summary.

**Problem:** Users could miss whether K stopped by objective saturation or by reaching Kmax.

**New behavior:** The run summary reports final K, candidate-space status, saturation boolean, full final starts, final SBAD_star, SBAD_limit, hybrid metrics, support-site SBAD reduction, proxy status, runtime, and cache diagnostics.

**Statistical or computational rationale:** The summary now surfaces the conditions that materially affect confidence in the selected field plan.

## 17. New cache and screening diagnostics added

**Old behavior:** Support cache behavior, batched optimizer stability, and bounded support-site candidate counts were not fully exposed.

**Problem:** Efficiency changes need audit trails so runtime improvements do not obscure the exact objective.

**New behavior:** v2.10 exports updated support-resolution, candidate-saturation, optimizer-stability, and support-site CSV columns, plus metadata cache statistics.

**Statistical or computational rationale:** Diagnostics make the adaptive decisions reproducible and reviewable.
