# ESAP RSSD v2.9 Methods

## 1. Purpose and ordinary-regression motivation

ESAP RSSD v2.9 selects a small calibration sample from a spatially referenced sensor survey for later ordinary regression calibration. The design is model-based and directed: it is intended to represent the sensor predictor space needed to identify and estimate a low-order calibration model while reducing the chance that future ordinary-regression residuals are strongly dependent because selected calibration sites are too clustered.

The workflow does not require the downstream analyst to fit a Gaussian process, kriging model, GLS covariance structure, or spatial error model. Spatial regression remains a fallback after measured response data and residual diagnostics show a need for it.

## 2. Statistical foundation in Lesch 1995 and Lesch 2005

The implementation follows the Lesch response-surface sampling framework: sensor measurements are standardized and decorrelated with PCA, theoretical response-surface targets are specified in coded predictor space, observed survey records near those targets are identified, and spatial criteria are used to choose physically separated calibration locations.

The 1995 Lesch, Strauss, and Rhoades paper motivates calibration-site selection for multiple linear regression and includes an average-distance spatial-uniformity criterion. The 2005 Lesch paper gives the sensor-directed response-surface sampling workflow and the geometric mean nearest-neighbor separation criterion used here as exact geoMSD.

## 3. Predictor standardization and PCA

The notebook preserves v2.8 feature handling. User-selected features are converted to numeric finite values, optional explicit transformations are applied, `StandardScaler` centers and scales the transformed variables, and PCA is fitted in either full or incremental mode depending on memory settings.

Retained design-PC scores are divided by the square root of the fitted PCA explained variance. This produces coded PC scores with approximately zero mean, unit sample standard deviation, and negligible retained-PC correlations.

## 4. Standardized PC response-surface geometry

The response-surface design is built in standardized retained-PC coordinates. Euclidean distances from theoretical targets are therefore measured in common coded PC units.

The empirical design radius is the configured quantile of the retained-PC radial distances. Cube and axial CCD points share that outer radius; center points remain at the origin.

## 5. Outlier masking

PCA-space outliers are flagged with a chi-square radial screen in retained standardized PC space. They are masked from response-surface candidate selection by default, but they are not treated as deletions from the source dataframe.

In v2.9, the geographic support domain is conceptually separate from the response-surface candidate domain. The current notebook builds the support sequence from complete finite analysis rows after raw filtering and coordinate validation; PCA-space outliers remain eligible for geographic support representation in the support-sequence construction.

## 6. CCD construction

For one to four retained design PCs, v2.9 keeps the v2.8 full second-order central composite design:

- all factorial cube points;
- two axial points per retained PC;
- a configurable number of center replicates, two by default.

For two PCs and two center replicates, the base CCD has 10 target instances.

## 7. Sample-budget decomposition

The default sample-budget mode is now `rssd_with_support`.

The full base response-surface CCD is preserved first. Additional samples may then be divided between augmented response-surface target instances and spatial support sites. The design never silently removes required CCD targets to make room for support sites.

`ccd_exact` remains available. `balanced_target_replication` remains available as a v2-compatible methodological comparison mode.

## 8. Response-surface target augmentation

After the base CCD is represented once, additional response-surface target instances are assigned deterministically and as evenly as possible across base targets. Repeated theoretical targets are allowed, but field observations must remain unique.

Every response-surface target row has `sample_role = "response_surface"`.

## 9. Spatial support sites

Spatial support sites are selected after the response-surface core is optimized. They are not assigned theoretical PC targets and are exported with `sample_role = "spatial_support"` and null target fields.

The implemented addition is sequential and gap-directed: after each addition, the support prefix is queried for the largest remaining nearest-final-site coverage distances, and the nearest unused eligible survey observation to a high-gap support point is added. Adding a support site cannot increase SBAD because the final selected set contains the previous selected set.

## 10. Classical ESAP AD

Classical ESAP used an average-distance criterion to assess spatial uniformity: survey support points were compared with their nearest selected calibration site, and smaller average distance indicated better coverage.

That formulation assumed a dense, centric, systematic grid where survey rows reasonably represented the spatial support of the field.

## 11. Limitation of raw observation-weighted AD

Modern inputs can be one-foot rasters, irregular EMI transects, vehicle paths, and nonuniform point clouds. A raw row-weighted AD score would let an oversampled transect dominate the geographic coverage objective solely because it contains more records.

v2.9 therefore does not use raw observation-weighted AD as the primary optimizer objective.

## 12. Spatially Balanced Average Distance

v2.9 implements Spatially Balanced Average Distance:

```text
SBAD(S) = mean_b min_s ||u_b - s||
```

where `u_b` are coordinates from a spatially balanced geographic support sequence and `s` are selected calibration sites. Lower SBAD means better field-wide geographic coverage.

This is documented as a methodological generalization of the classical ESAP AD criterion for non-systematic and unequal-density sensor surveys, not as a claim of global novelty across all spatial sampling literature.

## 13. ESAP 2 principle

ESAP 2 separates geographic support from sensor observation density. The row density of the sensor log is not allowed to be the geographic weight of the AD-style objective.

## 14. Nested geographic support sequence

One shared support sequence is built after survey validation and coordinate processing. It depends only on projected X/Y coordinates.

The implemented algorithm is deterministic recursive occupied-space bisection:

1. unique finite survey coordinates are sorted with stable index tie-breaking;
2. the root representative is the observed coordinate nearest the root bounding-box center;
3. the largest occupied leaf by bounding-box diagonal is repeatedly split;
4. the split axis is the axis with largest observed span;
5. the split threshold is the midpoint of observed min and max on that axis, not the observation median;
6. the child containing the existing representative keeps it;
7. the other nonempty child receives the observed coordinate nearest its child bounding-box center;
8. that new representative is appended to the master support sequence.

Prefixes define support resolutions, so `U_5000` is nested in `U_10000`, and so on when enough unique coordinates exist.

## 15. Adaptive SBAD support resolution

The default support mode is adaptive. Prefixes grow from `AD_SUPPORT_START_SIZE` by `AD_SUPPORT_GROWTH_FACTOR` to `AD_SUPPORT_MAX_SIZE`.

At each stage, v2.9 runs an AD-reference optimizer and a hybrid optimizer, retaining bounded panels of converged designs. Adjacent stages are compared by:

- relative change in best AD-reference SBAD;
- Spearman rank correlation of SBAD values over the retained panel union;
- whether the preferred hybrid design materially changed.

If stability is not confirmed by the maximum prefix, the run continues with the maximum prefix and reports `ad_support_resolution_stable = False`.

## 16. Exact geoMSD

v2.9 preserves the v2.8 exact cKDTree calculation of Lesch Eq. 9 geoMSD. A tree is built only on the selected calibration sites. Querying `k=2` returns each site's nearest other selected site, and geoMSD is the geometric mean of those nearest-neighbor distances.

## 17. AD-reference optimization

For a fixed support prefix, the AD-reference optimizer minimizes exact SBAD under the same PCA target candidate constraints used by the response-surface design.

Ties are resolved lexicographically:

1. minimize SBAD;
2. maximize exact geoMSD;
3. maximize absolute minimum selected-site separation;
4. minimize mean PCA target distance;
5. minimize maximum PCA target distance.

The AD-reference design is an internal reference and warm start.

## 18. Coverage envelope

The best AD-reference SBAD is `SBAD_star`. The hybrid coverage envelope is:

```text
SBAD_limit = (1 + AD_COVERAGE_ENVELOPE_REL_TOL) * SBAD_star
```

The run reports `core_coverage_ratio = SBAD / SBAD_star`.

## 19. Hybrid SBAD-constrained geoMSD optimization

The recommended v2.9 response-surface core is selected by maximizing exact geoMSD inside the SBAD coverage envelope. Among feasible designs, ties are resolved by minimum separation, mean PCA mismatch, and maximum PCA mismatch.

No arbitrary weighted sum of SBAD and geoMSD is used.

## 20. Adaptive candidate-space saturation

Candidate pools are nested. For each unique theoretical target, v2.9 builds a candidate sequence once and lets replicated target instances share that sequence. Candidate count grows by configured K stages until assignment is possible and a confirmation stage detects no new unique candidates, or the maximum K is reached.

The implementation records `ESAP_RSSD_candidate_saturation.csv`.

## 21. Adaptive optimizer initialization stability

AD-reference and hybrid optimizers use multiple starts: minimum PCA-distance assignment, warm starts, and reproducible random unique assignments. Coordinate exchange converges when a complete sweep accepts zero swaps.

Optimizer stability is reported separately in `ESAP_RSSD_optimizer_stability.csv`.

## 22. Sequential support-site addition

Support sites are added after the hybrid response-surface core. Each addition targets a current field-coverage gap in the final SBAD support prefix and records SBAD before and after addition.

## 23. Proxy spatial-scale diagnostic

The proxy diagnostic now uses the shared spatial support prefix rather than a simple random row sample. It builds per-PC semivariogram-like lag summaries from support-coordinate pairs.

## 24. Why proxy range is not residual range

The diagnostic uses sensor-PC predictors before response samples exist. It does not estimate the future regression residual correlation range and never changes the hybrid objective.

## 25. Regression-design diagnostics

The notebook preserves v2.8 regression-design diagnostics: second-order model matrix rank, condition number, leverage when estimable, and chunked average relative prediction variance. v2.9 evaluates these diagnostics on all final calibration sites, including spatial support sites.

## 26. Computational scaling

The implementation avoids survey-wide pairwise distance matrices, survey covariance matrices, Cartesian products of candidate pools, raster reshaping, FFT raster autocorrelation, and enumeration of all spatial pairs.

SBAD swap evaluation is exact for a fixed support prefix. It maintains nearest, second-nearest, and nearest-site identity vectors for support points and lazily caches support-to-candidate distance vectors.

## 27. Memory behavior

Candidate-to-support distance vectors are cached in `float32` with an LRU-style bounded cache controlled by `AD_DISTANCE_CACHE_MAX_MIB`. SBAD means and objective comparisons use `float64`.

The support sequence and candidate information are reused across support-resolution stages.

## 28. Applicability

The spatial support sequence uses only X/Y coordinates and makes no raster, row-column, constant-spacing, or transect-count assumption. It is applicable to rasters, transects, vehicle paths, and irregular point surveys as long as coordinates are projected in linear units.

## 29. Existing-location behavior

The guided workflow cells are preserved. Existing locations can still be entered and matched to nearest eligible survey observations. The v2.9 run wrapper currently preserves the workflow state pathway; forced-location handling should be reviewed for high-stakes runs because the implementation report flags it as partially validated.

## 30. Statistical assumptions

- Sensor covariates are relevant to the future response.
- A low-order response-surface regression is a reasonable calibration starting point.
- Standardized PC geometry is a meaningful coding of predictor conditions.
- Coordinates are projected in linear units.
- Increased spacing and improved coverage improve the chance of ordinary-regression residual independence, but do not prove it.

## 31. Limitations

The optimizer is a bounded local coordinate-exchange search, not a global combinatorial proof. Support-site addition is sequential and gap-directed, not a full global mixed-role optimizer. The support sequence is spatially balanced by recursive bisection, not by a formal spatially balanced probability design.

## 32. Post-calibration residual diagnostics

Residual plots, leverage checks, normality checks, and spatial residual diagnostics such as Moran's I remain post-calibration tasks after response measurements are collected and the calibration model is fitted.

## 33. Differences from classical ESAP

v2.9 keeps the response-surface foundation but generalizes the AD-style coverage objective to unequal-density modern surveys, uses exact tree-based geoMSD, uses adaptive support resolution, and exports complete modern provenance.

## 34. Differences from v2.8

v2.8 optimized geoMSD as the primary spatial objective. v2.9 first finds a near-best SBAD coverage reference and then maximizes geoMSD inside that coverage envelope. v2.9 also adds default spatial support-site allocation, support-sequence exports, candidate-saturation exports, optimizer-stability exports, and shared-support proxy diagnostics.

## 35. Planned validation

Planned validation should compare v2.9 against classical RSSD and spatial simulated annealing / MWMSD approaches on shared survey inputs, including target mismatch, SBAD, geoMSD, minimum separation, regression diagnostics, coverage-distance tails, runtime, and post-calibration residual diagnostics when measured responses are available.

## Key ESAP 2.9 methodological generalizations

- standardized PC coding corrected and generalized from the v2 line;
- exact tree-based geoMSD preserved;
- adaptive candidate-space exploration;
- spatially balanced AD-style coverage independent of raw observation density;
- adaptive support-resolution stability checks;
- AD-constrained geoMSD hybrid optimization;
- generalized spatial support-site allocation;
- topology-agnostic handling of dense rasters and irregular transects.

These are substantive generalizations of the classical ESAP workflow. They are not presented as universally novel spatial statistics without a dedicated literature review.
