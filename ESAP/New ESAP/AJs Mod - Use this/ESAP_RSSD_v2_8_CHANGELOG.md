# ESAP RSSD v2.8 changelog

This document compares `Sensor_Directed_Sampling.ipynb`, `AJ_Copy_of_Sensor_Directed_Sampling.ipynb`, `ESAP_RSSD_v2_scalable.ipynb`, and `ESAP_RSSD_v2_8_scalable.ipynb`. Entries 1-28 are retained from the v2 modernization history. Entries 29 onward describe the v2.8 revision. Each entry describes implemented behavior, not planned functionality.

## 1. Full survey-by-survey geographic distances removed

**Old behavior:** The original notebook called `distance_matrix(Geo_space_XY, Geo_space_XY)` to obtain global extrema. The AJ copy removed one active dense call but retained dense-distance imports/comments and replaced the scale with extrema of dense-pixel nearest-neighbor spacing.

**Problem:** An *N* by *N* matrix has quadratic RAM and time cost and is infeasible for high-density drone data. Dense-pixel spacing is also not calibration-site spacing.

**New behavior:** Candidate search uses cKDTree in PC space. Geographic calculations occur only within target neighborhoods or on the selected calibration set. No survey-wide spatial distance matrix is materialized.

**Statistical or computational rationale:** The method requires minimum separation among selected sites, not all pairwise survey distances. Tree queries preserve the relevant quantity with near-linear storage.

## 2. Millions-of-combinations materialization removed

**Old behavior:** The original notebook generated combinations in a set and converted up to 4.6 million combinations to an array. The AJ version streamed proposals but still attempted millions of full designs.

**Problem:** Materialization can exhaust RAM; streamed exhaustive-scale random evaluation still wastes computation and offers no systematic convergence.

**New behavior:** A coordinate-exchange optimizer evaluates one target-specific site swap at a time.

**Statistical or computational rationale:** Sequential site swaps follow the search logic described by Lesch and scale with starts, targets, and small candidate pools rather than the Cartesian product.

## 3. Random 33 percent combination search removed

**Old behavior:** The AJ generator evaluated `min(num_combs, total_combs * 0.33)` randomly sampled complete combinations.

**Problem:** The 33% fraction was arbitrary, could still imply millions of evaluations, and did not ensure local optimality or unique site assignments.

**New behavior:** One minimum-mismatch assignment and reproducible random unique assignments initialize repeated coordinate-exchange runs, each continued to a no-improvement sweep.

**Statistical or computational rationale:** Multiple converged starts address local optima more directly than an arbitrary fraction of random complete designs.

## 4. PCA score standardization corrected

**Old behavior:** Both legacy notebooks standardized input features but used ordinary `PCA.fit_transform` scores for target geometry. Those scores have unequal component variances.

**Problem:** Euclidean distance and CCD levels were evaluated on axes with inconsistent scales, contrary to Lesch's requirement for zero-mean, unit-variance PC scores.

**New behavior:** Retained PCA scores are divided by the square root of their explained variances. Means, sample standard deviations, and correlations are validated numerically.

**Statistical or computational rationale:** The resulting coordinates are coded, decorrelated variables in which Euclidean target distance has a consistent interpretation.

## 5. Marginal IQR filtering replaced

**Old behavior:** The primary legacy path used independent lower and upper IQR limits on each PC. The original notebook also exposed alternative methods inconsistently.

**Problem:** Rectangular marginal cutoffs do not represent multivariate radial extremeness in decorrelated standardized space.

**New behavior:** v2 uses \(D_i^2 = \sum_j PC_{ij}^2\) and a configurable chi-square threshold with retained-PC degrees of freedom. Outliers are flagged and masked, not deleted.

**Statistical or computational rationale:** The screen is a transparent multivariate distance rule aligned with standardized PC geometry.

## 6. Dense-pixel nearest-neighbor geographic scaling removed

**Old behavior:** The AJ notebook computed minimum and maximum nearest-pixel distances across the complete raster and used them to scale calibration-site separation.

**Problem:** Pixel spacing and selected calibration-site spacing are different quantities. Scaling by raster resolution can distort the optimization objective.

**New behavior:** Exact geoMSD remains in projected coordinate units and is not min-max scaled.

**Statistical or computational rationale:** Lesch's Eq. 9 criterion is directly interpretable in field distance units.

## 7. Arbitrary weighted score replaced

**Old behavior:** A widget combined scaled minimum geographic distance and maximum PC mismatch with a user-selected weight.

**Problem:** The result depended on arbitrary weights and on unrelated scale extrema.

**New behavior:** Candidate pools impose statistical proximity. Among valid unique designs, the optimizer maximizes geoMSD; mean and maximum PC mismatch are tie-breakers only.

**Statistical or computational rationale:** This separates response-surface fidelity as a constraint from spatial separation as the primary objective, matching Lesch's constrained design logic.

## 8. Moran's I site-selection objective removed

**Old behavior:** Legacy cells computed or proposed Moran's I on selected PC scores and included it in a weighted objective.

**Problem:** PC scores are predictors, not fitted calibration residuals. At sampling time, no response or residual exists.

**New behavior:** Moran's I is excluded, and the notebook explains its future role in calibration residual diagnostics.

**Statistical or computational rationale:** This restores the distinction in Lesch between site design and post-fit residual-independence assessment.

## 9. Ad hoc two-dimensional 20-point generator replaced

**Old behavior:** The legacy `generate_design` concatenated selected, halved pieces of a two-dimensional `ccdesign` result until an allowed sample count was approached.

**Problem:** The target set lacked a consistent CCD interpretation and did not generalize statistically to other dimensions or budgets.

**New behavior:** v2 constructs cube, axial, and explicit center targets on a common empirical radius.

**Statistical or computational rationale:** Every base target has a documented response-surface role and radial scale.

## 10. Multidimensional response-surface support added

**Old behavior:** Target generation was hard-coded to two PCs.

**Problem:** Modern multi-sensor proxy sets may need more than two coded design variables.

**New behavior:** Full CCD construction supports two to four design PCs, warns at four, and rejects larger full CCDs with guidance toward hybrid or small composite designs.

**Statistical or computational rationale:** The implementation generalizes the design while acknowledging exponential factorial growth and Lesch's high-dimensional guidance.

## 11. Balanced target replication added

**Old behavior:** Additional targets were assembled from rescaled CCD fragments.

**Problem:** Sample budgets above the base design had no transparent allocation rule.

**New behavior:** `balanced_target_replication` represents every base target and distributes extras evenly and deterministically. `ccd_exact` remains available.

**Statistical or computational rationale:** Repetition increases geographically distinct support for the same coded conditions without changing the theoretical target set.

## 12. Unique assignment, coordinate exchange, and multiple starts added

**Old behavior:** Independent nearest selections could overlap, and random complete proposals were not guaranteed to assign a unique survey site to each target.

**Problem:** Duplicate sites invalidate field plans and produce zero separation.

**New behavior:** Minimum-cost bipartite assignment enforces a unique initial site per target. Candidate pools expand automatically if needed. Multiple reproducible starts undergo coordinate exchange to convergence.

**Statistical or computational rationale:** The optimizer operates only on feasible one-to-one designs and reduces sensitivity to local optima.

## 13. Exact geoMSD and design diagnostics added

**Old behavior:** Optimization primarily used absolute minimum pairwise distance, with limited diagnostics.

**Problem:** Absolute minimum distance is Lesch's Eq. 10 criterion, not the requested Eq. 9 geometric mean criterion; model-matrix quality was not assessed.

**New behavior:** cKDTree calculates every selected site's exact nearest-neighbor distance and geoMSD. Outputs include minimum/mean/median separation, target mismatch, PC balance, second-order matrix rank and condition, leverage, and chunked avePVar.

**Statistical or computational rationale:** The primary criterion now matches Eq. 9, while diagnostics reveal spatial and regression-design weaknesses without changing the optimizer objective.

## 14. Reproducible metadata and run summaries added

**Old behavior:** AJ exports used timestamped result and parameter text files with incomplete computational/statistical provenance.

**Problem:** Exact reconstruction of a run was difficult.

**New behavior:** Stable CSV exports, a structured JSON metadata file, and a human-readable Markdown run summary record configuration, transformations, PCA, masking, targets, candidates, optimizer convergence, approximation flags, diagnostics, package versions, and seed.

**Statistical or computational rationale:** Complete provenance is necessary for defensible sampling plans and manuscript validation.

## 15. Fresh-runtime execution fixed

**Old behavior:** Widget and cell-order state, global variables, and manually triggered callbacks made execution order fragile.

**Problem:** A fresh runtime could reference unset values such as generated design arrays or `ndf`.

**New behavior:** A single configuration cell feeds deterministic functions and linear execution. The default synthetic demonstration lets a fresh Colab runtime execute top to bottom; real files use an explicit path or upload prompt.

**Statistical or computational rationale:** Reproducible execution prevents hidden state from changing a field design.

## 16. Unnecessary dependencies removed

**Old behavior:** Legacy imports included PySAL/esda, PyKrige, Shapely, seaborn, pyDOE3, and interactive widget infrastructure.

**Problem:** These packages increased setup time and failure modes despite not being required for the core RSSD method.

**New behavior:** v2 uses NumPy, pandas, SciPy, scikit-learn, and matplotlib, all normally available in Colab. Excel reading uses pandas' applicable engine only when needed.

**Statistical or computational rationale:** A smaller dependency surface improves portability and makes the implemented statistical operations easier to audit.

## 17. Optional large-data behavior made explicit

**Old behavior:** Dense data were either processed with quadratic operations or discussed in terms of ad hoc subsampling.

**Problem:** Data reduction could silently discard response-surface tails or rare conditions.

**New behavior:** Full-data analysis is the default. Auto memory estimation can select IncrementalPCA. A separately gated PCA-occupancy prefilter preserves strata, tails, and target neighborhoods and marks every approximate run. A disabled 300,000-row stress test reports memory and runtime.

**Statistical or computational rationale:** Efficient algorithms are the first defense. Any approximation that changes candidate discovery is explicit and separately validatable.

## 18. Guided Colab interface restored

**Old behavior:** The first v2 rebuild relied primarily on a configuration dataclass and therefore removed the upload, preview, column-selection, and visual controls used in both legacy notebooks.

**Problem:** Although reproducible, that interface made exploratory NDVI/NDRE workflows unnecessarily cumbersome and hid useful data-validation choices from non-programmatic users.

**New behavior:** A numbered, cell-by-cell `ipywidgets` workflow now supports primary and optional secondary CSV/Excel upload, cancel/reset buttons, dataframe and missing-value preview, optional existing locations, coordinate conversion, ID/X/Y assignment, geographic preview, multi-select PCA features, explicit per-feature transformations, PCA and design previews, sample controls, candidate/optimizer controls, memory settings, and plot colors. The last workflow cell finalizes the same dataclass consumed by the downstream analysis.

**Statistical or computational rationale:** Interactivity is restored at the input and presentation layers without restoring the legacy weighted objective, unwhitened PCA, Moran selection, or combinatorial search.

## 19. Single-proxy designs added

**Old behavior:** The first v2 notebook required at least two design PCs, preventing a direct NDVI-only or NDRE-only analysis.

**Problem:** A single dense proxy is a legitimate one-dimensional coded predictor and is central to the planned drone comparisons.

**New behavior:** One-PC quadratic CCD construction, plots, validation, optimization, diagnostics, and exports are supported. With two center replicates, the base design contains six targets: two instances at each outer level and two at the center.

**Statistical or computational rationale:** This provides the traditional six-site one-variable response-surface structure while preserving exact geoMSD optimization and unique field locations. For multiple PCs, the full-CCD minimum remains dimension-dependent rather than arbitrarily bypassed.

## 20. Decimal-degree to UTM conversion added

**Old behavior:** The AJ workflow displayed a UTM zone selector but did not integrate a general, validated conversion into the RSSD analysis. A separate helper script was hard-coded to UTM zone 13N and local filenames.

**Problem:** geoMSD in decimal degrees is not a defensible linear-distance criterion, while a hard-coded zone is not portable.

**New behavior:** The sequential workflow can transform selected WGS84 longitude/latitude columns with automatic centroid-based or manual UTM zone/hemisphere selection. It retains source coordinates, adds easting/northing, transforms entered existing locations consistently, and records the EPSG code.

**Statistical or computational rationale:** Exact geoMSD must be computed in projected linear units. Zone choice is explicit and no region-specific CRS is silently imposed.

## 21. Existing-location handling implemented

**Old behavior:** The AJ notebook accepted preferred coordinates and attempted to infer PC values through kriging before modifying candidate structures.

**Problem:** That path added kriging assumptions, could obscure whether sites were actually forced, and was not integrated with unique assignment.

**New behavior:** Entered locations are matched to unique eligible survey observations. Users choose ignore, evaluate/overlay, or force mode. Forced matches are assigned to target instances by minimum PCA distance, represented by singleton candidate pools, and remain locked during coordinate exchange. Matches and offsets are exported in metadata and selected-site flags.

**Statistical or computational rationale:** Existing sites are incorporated transparently without using kriged PC scores or weakening uniqueness checks. Any loss of response-surface fidelity remains visible in diagnostics.

## 22. Geographic previews and comparison boxplots restored

**Old behavior:** The first v2 rebuild produced final figures but omitted the staged geographic preview and familiar selected-versus-whole boxplot workflow.

**Problem:** Users could not visually catch coordinate-column mistakes early or compare the final calibration subset with the survey distribution in the familiar interface.

**New behavior:** An interactive geographic preview appears immediately after X/Y selection. Final output includes labeled selected-site maps plus side-by-side boxplots for standardized PCs and original sensor features.

**Statistical or computational rationale:** These plots improve quality control and interpretation while remaining diagnostics rather than optimization objectives.

## 23. Callback uploader replaced with one-file native Colab upload

**Old behavior:** A `FileUpload` widget and separate load button depended on Python callbacks. In some Colab sessions the browser displayed a selected-file count but neither the selection observer nor the load-button callback reached the kernel.

**Problem:** The interface appeared to accept a file while the Python dataframe remained unset. Adding a callback-driven progress bar could not solve a callback transport failure. The optional second file also added state without a defined role in RSSD.

**New behavior:** Running the upload cell directly calls `google.colab.files.upload()` and accepts exactly one complete survey file. Colab's native interface supplies file selection, byte-level progress, and cancellation. The notebook then prints transfer completion, filename, size, parsing state, row/column counts, and a preview. Synthetic demonstration and existing-path modes are selected through Colab form parameters. The second-file feature and callback loader are removed.

**Statistical or computational rationale:** This change does not affect analysis but makes file receipt synchronous and observable before configuration begins. It uses the same native mechanism as the working AJ notebook and eliminates ambiguous frontend-only widget state.

## 24. Two-dimensional response-surface preview clarified

**Old behavior:** The component selector could remain at one, producing a scientifically correct but visually unexpected PC1 line even when multiple features were available.

**Problem:** Users expected the familiar PC1-versus-PC2 response-surface scatter and could not tell why the view was one-dimensional.

**New behavior:** PCA preview defaults to two design PCs whenever at least two features exist. The interface explicitly explains one- versus two-dimensional modes. The two-dimensional preview adds the empirical radius and candidate-tolerance rings around CCD target crosses.

**Statistical or computational rationale:** Plot dimensionality now follows the selected design dimensionality transparently; no artificial PC2 axis is invented for a genuinely one-PC design.

## 25. Complete archival run bundle added

**Old behavior:** Individual CSV, JSON, and Markdown outputs were written, but displayed figures and auxiliary diagnostic tables were not collected into one archival artifact.

**Problem:** Reconstructing a run for manuscript preparation or later diagnosis required manually gathering files and screenshots.

**New behavior:** A final opt-in cell creates and downloads a timestamped ZIP containing core outputs, exact settings, metadata, convergence history, validation tables, a manifest, and twelve high-resolution diagnostic figures.

**Statistical or computational rationale:** A self-contained analysis record supports reproducibility, auditability, comparison among candidate designs, and later paper development without changing the site-selection algorithm.

## 26. Scientist-defined raw-data range filtering added

**Old behavior:** All finite uploaded sensor readings entered transformation, PCA, and statistical outlier screening. Removing known invalid measurements required editing the source file or notebook code.

**Problem:** Physically invalid values—such as negative EMI spikes over metal or vegetation-index values known to represent concrete or bare infrastructure—are domain exclusions, not statistical outliers. They can also invalidate later log transformations.

**New behavior:** A dedicated pre-PCA cell supports multiple interactive column rules with optional lower/upper bounds, inclusive/exclusive comparisons, and nonfinite handling. It previews retained/dropped counts and sampled distributions before an explicit apply action. Applied rules use AND logic, alter only the working dataframe, and are recorded in metadata, the run summary, and JSON/CSV files in the ZIP bundle.

**Statistical or computational rationale:** Domain-invalid measurements are removed before PCA geometry and chi-square screening are defined, keeping scientific validity filtering distinct from statistical outlier masking. Vectorized masks remain O(*N*) and are practical for large surveys.

## 27. Responsive widget layout added

**Old behavior:** Several controls were packed into fixed horizontal boxes. Colab's constrained output width could truncate dropdown and slider descriptions.

**Problem:** Hidden label text made otherwise interactive settings ambiguous, particularly for coordinate, design, and optimizer controls.

**New behavior:** Crowded controls use responsive grid layouts that automatically wrap according to available width. Description widths are set to their natural content size, and a small CSS rule permits long labels to wrap instead of being clipped.

**Statistical or computational rationale:** This is a presentation-only change that improves parameter transparency without modifying saved values or analysis behavior.

## 28. Labeled Google Earth KMZ export added

**Old behavior:** Selected sites were exported as CSV rows and projected-coordinate figures, requiring a separate conversion and placemark-building step before viewing them in Google Earth.

**Problem:** Field and manuscript workflows benefit from an immediately portable map layer, but a valid Google Earth layer cannot be generated unless the source projected coordinate reference system is known.

**New behavior:** Every successful run now writes `ESAP_RSSD_selected_sites.kmz` when a source EPSG is available. UTM conversion supplies that EPSG automatically; already-projected input has a new EPSG entry control. The KMZ transforms sites to WGS84, labels each placemark with sample order and sample ID, includes run-relevant site details in the popup, records export metadata, and is copied into the complete run ZIP.

**Statistical or computational rationale:** CRS-aware transformation prevents projected easting/northing values from being misinterpreted as longitude/latitude. The KMZ is an output representation only and does not alter RSSD selection or distance calculations.

## 29. Candidate-search sufficiency reporting added

**Old behavior:** v2 exported the optimizer convergence table but did not summarize whether the bounded candidate-pool and coordinate-exchange search appeared to have been explored sufficiently.

**Problem:** A scientist could see the starts and final geoMSD values but still had to manually judge whether more starts, wider candidate pools, or larger PCA tolerances were warranted before collecting field samples.

**New behavior:** v2.8 writes and displays a candidate-pool report and a search-sufficiency report. The report records pool sizes, tolerance use, nearest-*k* fallback flags, assignment-expansion attempts, best geoMSD, first and last best starts, starts since last improvement, near-best start count, and an interpretation status such as `plausibly_saturated_local_search`, `late_improvement_possible`, or `candidate_space_constrained`.

**Statistical or computational rationale:** The diagnostic does not prove global optimality, but it makes the bounded local-search evidence explicit and reproducible.

## 30. Stable-search early stopping added

**Old behavior:** v2 ran the configured number of optimizer starts and then reran the full optimizer a second time as a reproducibility assertion.

**Problem:** For field use, the second full optimizer run doubled optimization time, and a fixed number of starts could waste time after the best design had remained unchanged for many starts.

**New behavior:** v2.8 treats `N_OPTIMIZER_STARTS` as a maximum when `EARLY_STOP_ON_STABLE_SEARCH` is enabled. The optimizer runs at least `MIN_OPTIMIZER_STARTS` and stops after `OPTIMIZER_NO_IMPROVEMENT_PATIENCE` starts without a new best design. The deterministic reproducibility rerun remains available through `VERIFY_REPRODUCIBILITY_BY_RERUN` but is disabled by default.

**Statistical or computational rationale:** The seed, unique-assignment checks, convergence trace, and metadata preserve reproducibility while avoiding unnecessary same-day field runtime.

## 31. Proxy spacing plausibility diagnostic added

**Old behavior:** v2 reported geoMSD, minimum separation, mean/median nearest-selected-neighbor separation, and individual nearest-neighbor distances, but it did not evaluate whether those spacings were large relative to spatial structure in the sensor predictors.

**Problem:** Lesch separated calibration sites to improve the chance that later ordinary regression residuals would be approximately independent. Before response samples are collected, residuals do not exist, so Moran's I cannot answer this question at design time.

**New behavior:** v2.8 adds a pre-calibration proxy spacing screen. It samples coordinate pairs directly from projected X/Y values, combines local nearest-neighbor pairs with random long-distance pairs, calculates binned standardized-PC semivariance, estimates a proxy decorrelation distance, and compares selected-site minimum spacing, median spacing, and geoMSD with that distance.

**Statistical or computational rationale:** This is a plausibility screen for ordinary-regression independence risk, not a residual test and not an optimization objective. Residual diagnostics remain required after calibration.

## 32. Irregular point, transect, and point-cloud generality preserved in spacing diagnostics

**Old behavior:** v2 avoided full survey distance matrices and raster assumptions in the RSSD optimizer, but it had no pre-calibration spacing diagnostic.

**Problem:** A new spacing diagnostic could have accidentally assumed gridded pixels, fixed row/column offsets, constant nearest-neighbor spacing, or raster autocorrelation.

**New behavior:** v2.8's spacing diagnostic uses only supplied projected coordinates, cKDTree nearest-neighbor pairs on a reproducible subset, and random coordinate pairs. It does not infer rows or columns, reshape data, use `np.roll`, use FFT autocorrelation, or assume systematic sampling.

**Statistical or computational rationale:** The same notebook remains usable for drone rasters, irregular point observations, EMI transects, vehicle paths, and variable-density point clouds.

## 33. Metadata and run bundle expanded for v2.8 diagnostics

**Old behavior:** v2 saved selected sites, candidate sites, optimizer convergence, metadata, summary, figures, and optional KMZ.

**Problem:** The new sufficiency and spacing diagnostics need to be auditable outside the live notebook session.

**New behavior:** v2.8 writes `ESAP_RSSD_candidate_pool_report.csv` and `ESAP_RSSD_spacing_semivariogram.csv` when applicable. Metadata now includes `candidate_search_sufficiency`, the candidate-pool report, `spacing_diagnostic`, and the spacing semivariogram. The ZIP bundle includes search-sufficiency JSON, spacing-diagnostic JSON, the candidate-pool CSV, the spacing-semivariogram CSV, and an additional proxy spacing figure.

**Statistical or computational rationale:** The same evidence used to accept or revise a same-day sampling plan is preserved for later audit, manuscript comparison, and troubleshooting.

## 34. Guided field controls updated

**Old behavior:** The final guided workflow cell exposed candidate counts, PCA tolerances, optimizer starts, memory mode, approximate prefiltering, existing-location mode, and plot colors.

**Problem:** v2.8 adds operational choices that field users need to see without editing code.

**New behavior:** The final workflow cell now exposes maximum starts, minimum starts, no-improvement patience, stable early stopping, optional reproducibility rerun, and the proxy spacing diagnostic toggle. The final applied-settings table records those choices before the analysis cells are run.

**Statistical or computational rationale:** Scientist-facing controls remain explicit and recorded while the numerical RSSD engine remains centralized in the same configuration object.
