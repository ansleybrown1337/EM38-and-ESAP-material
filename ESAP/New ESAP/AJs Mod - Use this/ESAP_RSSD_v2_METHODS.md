# ESAP RSSD v2: scalable response-surface sampling methods

## 1. Purpose and scope

ESAP RSSD v2 selects calibration sites from a dense, spatially referenced sensor survey. It is a model-based directed sampling procedure intended for situations in which a small set of measured responses will later be regressed on exhaustively observed sensor covariates. The implementation is designed for modern high-density proxy data, including electromagnetic induction measurements, drone spectral indices, canopy attributes, and terrain variables.

The method has two simultaneous goals. Selected observations should closely represent a prespecified response-surface design in standardized principal-component (PC) space, and their field locations should be geographically separated so that short-range correlation among future calibration-model residuals is less likely. Spatial dispersion alone is not ESAP RSSD; the response-surface representation constraint is essential.

## 2. Statistical foundation in Lesch (2005)

The implementation preserves the four-stage spatial response surface (SRS) procedure in Lesch (2005):

1. center, scale, and decorrelate the sensor matrix with principal components analysis (PCA);
2. specify a response-surface design in coded, standardized PC coordinates;
3. identify observed survey records close to the theoretical design levels; and
4. select one unique observation for each target with an iterative spatial optimization criterion based on minimum adjacent-site separation.

Lesch describes this as a constrained space-filling design: model-space representation is imposed by the response-surface targets and their candidate neighborhoods, while geographic separation is optimized within those constraints. The default nonparametric spatial criterion is the geometric mean of the minimum separation distances (Eq. 9 in Lesch, 2005).

## 3. Sensor data standardization and PCA

All configured features are first converted to numeric finite values. Optional feature transformations are explicit and independently configured as `none`, natural `log`, or `yeo-johnson`. No transformation is selected automatically. Raw and transformed skewness and feature histograms are reported to support an analyst's decision.

Transformed features are centered and standardized with a `StandardScaler`. PCA is then fitted to the standardized feature matrix. Full PCA is used by default when the estimated working arrays fit within the configured safe fraction of available memory. Incremental PCA is available for genuinely memory-constrained runs.

PCA is used as a rotation and coding operation, not merely as a dimension-reduction heuristic. The configured number of design PCs must not exceed the number of usable sensor variables. The implementation records the variance explained by every fitted component and the analysis mode used.

## 4. Standardized or whitened PCA score space

Ordinary PCA scores have variances equal to their component eigenvalues and therefore are not automatically coded to unit variance. For each retained design component, v2 divides the raw component score by the square root of its fitted explained variance. This gives retained design scores with approximately zero mean, unit sample standard deviation, and zero off-diagonal correlation.

The same operation is applied after full PCA and IncrementalPCA. A numerical validation table and correlation matrix are produced in every run. This standardization is necessary because Euclidean target distances and response-surface levels are interpreted in common standardized PC units.

## 5. PCA-space outlier screening

For observation *i* with *p* retained standardized design scores, v2 calculates

\[
D_i^2 = \sum_{j=1}^{p} PC_{ij}^2.
\]

The default threshold is the 0.999 quantile of a chi-square distribution with *p* degrees of freedom. This procedure assumes that the retained standardized PC distribution is approximately elliptical and that chi-square radial coverage is a useful screening model. It is a transparent statistical screen, not a claim that all sensor data are exactly multivariate normal.

Flagged observations remain in the source dataframe and receive `pca_space_outlier_flag = True`. They are masked from candidate selection by default. Missing or nonfinite required values are also retained in the source dataframe but excluded from numerical analysis.

## 6. Response surface design construction

Version 2 constructs a full second-order central composite design (CCD) in *p* standardized PC dimensions for *p* = 1, 2, 3, or 4. The one-PC case supports a single drone proxy such as NDVI or NDRE; the two-PC case supports joint designs from both proxies. The base design contains:

- all \(2^p\) cube or factorial points;
- \(2p\) axial points; and
- a configurable number of center replicates (two by default).

For one PC, cube and axial points coincide at the two outer levels, so the default design has two replicates at each outer level and two center points (six target instances). For two PCs, the default base design has four cube points, four axial points, and two center points. For three PCs it has eight cube, six axial, and two center points. A four-PC design is supported but produces a warning because full CCD size grows rapidly. Designs above four PCs are deliberately rejected; Lesch notes that hybrid or small composite designs may be preferable for four to six sensor dimensions.

## 7. Empirical design radius

Let \(r_i = \lVert PC_i \rVert_2\) be the radial distance of each complete survey observation in standardized design-PC space. The design radius *R* is the empirical `DESIGN_COVERAGE` quantile of these radii, with a default coverage of 0.80. Axial points are placed at \(\pm R\) on one axis and zero on the remaining axes. Cube coordinates are \(\pm R/\sqrt{p}\) on every axis, so every outer cube and axial target has radius *R*.

This generalizes the adjustment in Lesch's bivariate illustration, where the response-surface design was scaled to encompass approximately 80% of the transformed survey distribution. The notebook reports *R*, realized empirical coverage, and counts of cube, axial, center, base, and replicated target points.

## 8. Sample budget and balanced target replication

Two explicit sample-budget modes are implemented.

`ccd_exact` uses every base CCD target exactly once and ignores a conflicting `N_SAMPLES` value with a visible message.

`balanced_target_replication` requires at least as many samples as base targets. It assigns one instance to every base target, distributes remaining instances as evenly as possible in stable target order, and records every replication count. Repeated theoretical targets are allowed; selected field observations are always unique. For two design PCs, 10 base targets, and 20 samples, each base target is represented twice.

Balanced replication is a deliberate generalization for budgets larger than the minimum CCD. It does not imply that repeated field observations are permitted. Multiple geographically distinct locations instead represent approximately the same coded sensor condition.

With two center replicates, the full-CCD minimum is 6, 10, 16, or 26 samples for one, two, three, or four design PCs, respectively. The sample budget may be any integer at or above the applicable minimum. A smaller budget would require a separately specified reduced, hybrid, or small composite design; changing the sample count alone cannot preserve the full CCD.

## 9. Candidate site identification

A `scipy.spatial.cKDTree` is built on all eligible standardized design-PC observations (or on the explicitly marked approximate prefilter result). Each target begins with `PC_CANDIDATE_TOLERANCE = 0.15` standardized PC units by default. If too few observations occur within the radius, tolerance expands geometrically and deterministically up to the configured limit. A final nearest-*k* fallback is visible and recorded if the limit still cannot supply the required pool.

The observation with minimum exact Euclidean PC distance is retained first. Additional candidates are selected greedily from the target neighborhood to maximize their minimum geographic distance from candidates already retained for that same target. PCA distance and stable source order break geographic ties. This implements Lesch's large-survey recommendation while avoiding survey-wide geographic pairwise distances.

Identical replicated targets share statistical neighborhoods, so their minimum pool size is automatically increased when needed to permit unique assignments. Candidate pools may overlap. A minimum-cost bipartite assignment (`linear_sum_assignment`) finds the unique assignment with minimum total PC mismatch. If no complete assignment exists, all pools are deterministically enlarged and assignment is retried. Failure after bounded expansion produces an explicit error rather than duplicated sites.

## 10. Exact nearest-neighbor computation of geoMSD

For a selected set of *m* field locations, define

\[
d_j = \min_{k \ne j} \lVert s_j-s_k \rVert_2,
\qquad
geoMSD = \exp\left(\frac{1}{m}\sum_{j=1}^{m}\log d_j\right).
\]

The code builds a cKDTree only on the *m* selected coordinates and queries `k = 2`. The first returned neighbor is the observation itself; the second distance is exactly \(d_j\). A unit test compares this result with a brute-force `pdist` calculation on a small synthetic set under strict floating-point tolerance.

The KDTree is an efficient way to calculate every selected site's exact minimum separation. Exact nearest-neighbor geoMSD is not an approximation to Lesch's Eq. 9 criterion. The computational implementation changes; the statistical criterion remains the geometric mean minimum separation distance.

Coordinates must be projected in linear units. A conservative longitude/latitude detector stops runs that strongly resemble decimal degrees and directs the analyst to an appropriate projected coordinate reference system, such as the applicable UTM zone. No UTM zone is hard-coded.

## 11. Coordinate-exchange optimization

The first optimizer start is the minimum-PC-distance unique bipartite assignment. Remaining starts use reproducible random costs in the same bipartite assignment, which generates unique alternatives without enumerating a Cartesian product. All random operations use `RANDOM_SEED`.

For every start, target positions are visited in a reproducibly shuffled order. At one position, every alternative in that target's candidate pool is tested. Sites already used by another target are rejected. Membership in the tolerance-constrained target pool enforces target matching. The proposal with the best valid lexicographic rank is accepted. Complete sweeps continue until a sweep accepts no exchange or the configured sweep limit is reached.

Valid designs are ranked as follows:

1. maximize exact geoMSD;
2. when geoMSD differs by no more than the configured relative tie tolerance, minimize mean Euclidean PC target distance; and
3. if still tied, minimize maximum PC target distance.

No arbitrary weighted sum is used. The convergence table records start type, initial and final geoMSD, swaps, sweeps, and final mean and maximum target mismatch.

## 12. Why this implementation does not require an N by N spatial distance matrix

No operation calculates all pairwise distances among survey observations. PC target searches use a cKDTree. Geographic spreading inside one target pool compares candidate coordinates only with the small set already retained for that target. Exact geoMSD builds a tree on the selected set, whose size is the calibration budget rather than survey size. Regression diagnostics use cross-products and row-wise quadratic forms in chunks.

The main numerical storage therefore scales approximately linearly with the number of survey rows for a fixed number of features and design PCs. The optimizer scales with target count, candidate-pool sizes, and starts; it does not scale with the Cartesian product of pools.

## 13. Why Moran's I is excluded from site selection

The Moran statistic discussed by Lesch is a residual diagnostic after a response variable has been measured and a calibration regression has been fitted. At site-selection time, no fitted calibration residuals exist. PC scores are coded predictor values, not regression residuals. Optimizing Moran's I on those scores would substitute a different objective for the published SRS logic.

Version 2 therefore does not calculate Moran's I and does not install PySAL or `esda`. Residual spatial dependence must be evaluated in the future calibration and validation workflow.

## 14. Memory scaling and large-data behavior

The complete valid dataset is used by default. `float32` arrays store transformed features, coordinates, and design scores where their precision is adequate. Pandas copies are limited to validation and export structures. Full survey distance matrices and complete design combinations are absent.

`MEMORY_MODE = "auto"` estimates memory for transformed, standardized, PCA working, and retained-score arrays and compares it with a configurable fraction of available RAM. Full-data scaling and PCA remain the preferred path for ordinary datasets around 300,000 rows with a modest feature count. Incremental scaling and IncrementalPCA are selected only when the estimate exceeds the safety allowance, or when explicitly requested. Incremental transformed scores are divided by the square roots of IncrementalPCA explained variances exactly as in full mode.

Average relative prediction variance is evaluated in chunks. Plotting uses a reproducible display subset only and does not alter the analysis population. An optional disabled 300,000-row synthetic stress test reports elapsed time and major-array memory.

The Colab notebook also provides an `ipywidgets` guided setup panel. File upload and path input, dataframe preview, role-column assignment, multi-select PCA features, per-feature transformations, design-PC count, sample budget, design coverage, outlier coverage, candidate settings, optimizer starts, memory mode, approximation permission, and plot colors are exposed interactively. Applying the panel updates the same recorded configuration object used by scripted runs; the statistical engine is not duplicated.

## 15. Optional approximate PCA-space prefilter

`ALLOW_APPROXIMATE_PREFILTER` is `False` by default. When enabled and the eligible population exceeds its trigger, the fallback bins observations by multidimensional PC quantiles, retains a capped reproducible sample from every occupied stratum, explicitly retains univariate PC tails, and explicitly retains every observation inside each initial response-surface target neighborhood.

This preserves central occupancy, tails, low-frequency occupied regions, and target neighborhoods more deliberately than simple random or geographic-only subsampling. Nevertheless, it changes the population passed to expanded candidate discovery and is not mathematically identical to using the complete survey. Every affected run is marked `approximate_candidate_prefilter = true` in metadata and the run summary.

## 16. Design diagnostics

Final spatial diagnostics include geoMSD, absolute minimum separation, mean and median nearest-selected-neighbor separation, and each individual nearest-neighbor distance. Model-space diagnostics include mean and maximum target mismatch, PC balance (the Euclidean norm of mean selected standardized PC scores), outlier count, and empirical design-radius coverage.

A full second-order polynomial matrix is formed from selected design PCs with intercept, linear terms, squared terms, and all pairwise interactions. The notebook reports matrix rank and condition number. If full rank, it calculates selected-site leverage, maximum leverage, and average relative prediction variance over all eligible observations:

\[
avePVar = \frac{1}{N}\sum_{i=1}^{N} \left[1 + x_i^T(X^TX)^{-1}x_i\right].
\]

Population rows are processed in chunks; no *N* by *N* hat matrix is created. If the selected model matrix is rank deficient, inverse-based results are not calculated and the deficiency is reported prominently. These are diagnostics, not replacements for geoMSD optimization.

## 17. Statistical assumptions

- Dense sensor covariates are measured consistently and are relevant predictors of the future response.
- Configured transformations and a low-order second-order model are reasonable for calibration-model exploration.
- Standardized design-PC geometry is a meaningful way to represent predictor conditions.
- The selected empirical design coverage and candidate tolerances are scientifically appropriate for the survey.
- Coordinates are projected in linear units and exact duplicate coordinates should not represent independent sample locations.
- Increasing geographic separation makes short-range residual correlation less likely, but does not prove residual independence.
- The chi-square radial outlier screen is an approximate elliptical-distribution model.

## 18. Limitations

The design is model-based and directed. Selected sites are not, by themselves, a probability sample supporting unbiased design-based population estimates. Results depend on chosen features, transformations, retained PC count, design coverage, candidate tolerance, and sample budget. A full CCD can become inefficient in higher dimensions, and four-PC support should not be interpreted as a universal recommendation.

Coordinate exchange can converge to a local optimum; multiple starts reduce but do not eliminate that risk. Candidate restrictions trade exact target matching against possible spatial separation. Residual independence remains an empirical property of the future fitted model and must be checked after response collection.

## 19. Differences from classical ESAP software

Version 2 retains Lesch's SRS logic but provides transparent Python configuration, generalized multi-feature PCA inputs, empirical-radius CCD construction through four PCs, explicit balanced target replication, exact tree-based geoMSD, multiple-start coordinate exchange, large-data memory modes, reproducible metadata, and modern regression-design diagnostics. It does not reproduce undocumented interface defaults or binary file conventions from classical software.

The generalized target replication mode and optional approximate candidate prefilter are new. Neither should be described as an exact reproduction of every classical ESAP design. The core response-surface constraints and Eq. 9 separation criterion remain unchanged.

## 20. Differences from the previous AJ notebook

The AJ notebook used ordinary unwhitened PCA scores, marginal IQR screening, ad hoc pieces of a two-dimensional CCD, dense-pixel nearest-neighbor extrema for geographic score scaling, a user-weighted combination of minimum distance and target mismatch, random evaluation of up to 33% of millions of site combinations, and an optional Moran objective on PC scores.

Version 2 replaces those elements with standardized PC scores, multivariate chi-square radial screening, a mathematically defined multidimensional CCD, an unscaled exact geoMSD objective, candidate-constrained lexicographic optimization, unique assignment, coordinate exchange, and post-calibration-only Moran guidance. Unneeded kriging, shapely, PySAL, seaborn, and pyDOE dependencies are removed. `ipywidgets` is retained only for the guided Colab interface and does not participate in the numerical method.

## 21. Planned validation against classical RSSD

Planned scientific validation should use common survey inputs and fixed response-surface specifications to compare classical ESAP and v2 on target mismatch, individual minimum separation distances, geoMSD, matrix rank, condition number, leverage, avePVar, and computation time. When measured response data are available, both designs should also be compared on calibration accuracy and fitted residual spatial diagnostics. Optional approximate-prefilter runs require a separate comparison with complete-data candidate discovery.

## Reference

Lesch, S. M. (2005). Sensor-directed response surface sampling designs for characterizing spatial variation in soil properties. *Computers and Electronics in Agriculture*, 46, 153-179. https://doi.org/10.1016/j.compag.2004.11.004
