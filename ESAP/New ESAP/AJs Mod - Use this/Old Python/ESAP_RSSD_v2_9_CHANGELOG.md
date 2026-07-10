# ESAP RSSD v2.9 changelog

This changelog compares `ESAP_RSSD_v2_8_scalable.ipynb` with `ESAP_RSSD_v2_9_scalable.ipynb`. Each item describes old behavior, problem, new behavior, and statistical or computational rationale.

## 1. Primary optimization criterion

**Old behavior:** v2.8 maximized exact geoMSD as the primary spatial objective under PCA target constraints.

**Problem:** geoMSD separates selected sites but does not directly measure field-wide geographic coverage gaps.

**New behavior:** v2.9 finds an AD-reference SBAD optimum, defines a near-optimal SBAD envelope, then maximizes exact geoMSD inside that envelope.

**Statistical or computational rationale:** Predictor-space representation, field-wide coverage, and selected-site separation are separate design goals.

## 2. Classical AD generalized

**Old behavior:** v2.8 did not optimize AD-style coverage.

**Problem:** Classical raw-grid AD cannot be directly applied to irregular or unequal-density modern sensor surveys without row-density bias.

**New behavior:** v2.9 implements Spatially Balanced Average Distance, SBAD.

**Statistical or computational rationale:** SBAD generalizes classical ESAP AD to a spatially balanced support sequence.

## 3. Geographic support separated from sensor observation density

**Old behavior:** v2.8 avoided AD entirely.

**Problem:** Restoring raw row-weighted AD would overweight oversampled transects.

**New behavior:** v2.9 builds a support sequence from X/Y geometry only.

**Statistical or computational rationale:** ESAP 2 separates geographic support from sensor observation density.

## 4. Nested spatial support sequence

**Old behavior:** v2.8 had no shared nested support sequence.

**Problem:** Independent subsamples for diagnostics and optimization would make coverage quantities inconsistent.

**New behavior:** v2.9 builds one deterministic recursive occupied-space bisection support sequence.

**Statistical or computational rationale:** Prefixes support SBAD optimization, diagnostics, gap identification, proxy scale diagnostics, and coverage maps.

## 5. Adaptive SBAD support resolution

**Old behavior:** v2.8 had no support-resolution decision.

**Problem:** A fixed arbitrary support size can change optimizer decisions.

**New behavior:** v2.9 evaluates nested support prefixes and exports `ESAP_RSSD_ad_support_resolution.csv`.

**Statistical or computational rationale:** The coverage objective is used only after decision stability is checked or instability is reported.

## 6. Fixed candidate count replaced with candidate saturation

**Old behavior:** v2.8 used a configured candidate count per target, with assignment-driven enlargement.

**Problem:** Candidate adequacy and optimizer convergence were partly intertwined.

**New behavior:** v2.9 records nested K-stage candidate expansion in `ESAP_RSSD_candidate_saturation.csv`.

**Statistical or computational rationale:** Candidate-space exploration is documented separately from optimizer initialization stability.

## 7. Replicated-target candidate discovery

**Old behavior:** v2.8 could rediscover equivalent neighborhoods for identical replicated targets.

**Problem:** Duplicate target discovery wastes time and can obscure nesting.

**New behavior:** v2.9 builds one candidate sequence per unique theoretical target and shares it across replicated target instances.

**Statistical or computational rationale:** Replicated target instances should reference common base-target candidate sequences.

## 8. Greedy candidate distance update

**Old behavior:** v2.8 recomputed geographic distance from remaining candidates to every retained candidate at each greedy step.

**Problem:** That repeated work was unnecessary.

**New behavior:** v2.9 maintains an incremental minimum-distance vector for the target neighborhood.

**Statistical or computational rationale:** The candidate sequence is the same greedy farthest-point sequence, but computed more efficiently.

## 9. Balanced target replication demoted

**Old behavior:** `balanced_target_replication` was the default sample-budget mode.

**Problem:** It allocated the entire budget to response-surface target instances.

**New behavior:** `rssd_with_support` is the default.

**Statistical or computational rationale:** Modern RSSD should reserve a small portion of the budget for geographic coverage gaps when the base CCD permits it.

## 10. Spatial support-site allocation added

**Old behavior:** v2.8 had no explicit support-site role.

**Problem:** Extra samples could not be devoted specifically to field-wide coverage.

**New behavior:** v2.9 adds `legacy_inspired_auto`, `manual`, and `none` support modes.

**Statistical or computational rationale:** The full response-surface core is preserved first; support sites use only extra budget.

## 11. Sequential support-site addition

**Old behavior:** v2.8 selected only response-surface sites.

**Problem:** Remaining coverage gaps after core optimization were not directly addressed.

**New behavior:** v2.9 adds spatial support sites after the hybrid core and records SBAD before and after each addition.

**Statistical or computational rationale:** Coverage gaps can be reduced without changing response-surface target membership.

## 12. Optimizer patience replaced by objective-aware stability reporting

**Old behavior:** v2.8 used no-improvement patience mainly for geoMSD starts.

**Problem:** AD-reference and hybrid objectives need distinct traces.

**New behavior:** v2.9 exports `ESAP_RSSD_optimizer_stability.csv` with `objective_type`.

**Statistical or computational rationale:** AD-reference and hybrid convergence evidence should be auditable separately.

## 13. Candidate saturation separated from optimizer convergence

**Old behavior:** v2.8 search sufficiency combined pool and optimizer information.

**Problem:** Candidate pool breadth and coordinate-exchange initialization are different concerns.

**New behavior:** v2.9 exports candidate saturation and optimizer stability as separate tables.

**Statistical or computational rationale:** A stable optimizer result does not prove candidate-space saturation.

## 14. Proxy spacing diagnostic sampling changed

**Old behavior:** v2.8 used a reproducible random subset of raw eligible rows.

**Problem:** Raw row sampling can reflect sensor logging density.

**New behavior:** v2.9 uses the shared spatial support prefix.

**Statistical or computational rationale:** Proxy diagnostics should share the same density-balanced geographic support logic as SBAD.

## 15. Per-PC proxy semivariograms

**Old behavior:** v2.8 calculated one combined proxy semivariance.

**Problem:** Different retained PCs can have different spatial scales.

**New behavior:** v2.9 exports tidy per-PC lag summaries and reliability flags.

**Statistical or computational rationale:** A single pooled proxy scale can hide PC-specific structure.

## 16. Engine cells consolidated

**Old behavior:** v2.8 required separate imports/defaults/data/PCA/spatial/diagnostic definition cells.

**Problem:** Fresh execution required multiple silent engine cells.

**New behavior:** v2.9 has one consolidated engine initialization cell.

**Statistical or computational rationale:** Fewer hidden-state opportunities and clearer execution order.

## 17. Primary analysis cells consolidated

**Old behavior:** v2.8 numerical analysis ran across cells 2.1 through 2.7.

**Problem:** Internal numerical stages did not require user decisions.

**New behavior:** v2.9 wraps the numerical pipeline in `run_esap_rssd(...)` and exposes one primary analysis cell.

**Statistical or computational rationale:** User inspection remains for scientifically meaningful setup stages; numerical execution is centralized.

## 18. New coverage diagnostics and outputs

**Old behavior:** v2.8 exported selected sites, candidates, convergence, spacing semivariogram, metadata, summary, and bundle files.

**Problem:** SBAD and support-site decisions needed auditable tables.

**New behavior:** v2.9 adds support sequence, support-resolution, candidate-saturation, optimizer-stability, spatial-support-site, field-coverage-distance, and proxy-scale outputs. The notebook also restores live figure output and bundle PNG export for final maps, candidate maps, response-surface target matches, PC and feature boxplots, nearest-neighbor distances, optimizer traces, proxy spatial scale, SBAD support-resolution diagnostics, coverage-distance distributions, and support-site SBAD reductions.

**Statistical or computational rationale:** The new design decisions are reproducible outside the live notebook.

## 19. Survey-wide pairwise matrices still prohibited

**Old behavior:** v2.8 avoided survey-wide pairwise distance matrices.

**Problem:** Reintroducing AD could have encouraged dense survey-by-survey matrices.

**New behavior:** v2.9 calculates exact SBAD only between bounded support prefixes and selected/candidate sites.

**Statistical or computational rationale:** Exact fixed-support SBAD does not require an N by N survey distance matrix.

## 20. No required spatial regression downstream

**Old behavior:** v2.8 already excluded Moran's I and spatial regression from site selection.

**Problem:** The new spatial coverage objective could be misread as a spatial-modeling requirement.

**New behavior:** v2.9 explicitly states that ordinary regression remains the intended downstream default, with spatial residual diagnostics after calibration.

**Statistical or computational rationale:** RSSD is designed to improve the chance that ordinary regression assumptions are reasonable, not to replace residual diagnostics.
