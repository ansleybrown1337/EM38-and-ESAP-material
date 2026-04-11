# Global Synopsis: A Versioned Modernization of ESAP

## Framing

The ESAP framework was originally developed to enable cost-efficient spatial prediction of soil and crop properties using dense proximal sensing data and a limited number of calibration samples. Its central innovation lies in Response Surface Sampling Design (RSSD), which selects calibration locations that are both statistically representative and spatially separated to support regression-based prediction under minimal residual autocorrelation.

This paradigm remains highly relevant. In fact, it is arguably more valuable today given the explosion of high-density spatial data from drone imagery, proximal sensors, and IoT systems. However, the original ESAP implementation is computationally constrained, methodologically dated in its calibration approach, and not readily extensible to modern sensing systems.

This work proposes a structured modernization of ESAP through four sequential versions, each corresponding to a standalone, peer-reviewed contribution.

---

# Paper 1: Version 2.0 — Scalable ESAP-RSSD

## Core contribution
A computational redesign of ESAP-RSSD that preserves its statistical design principles while enabling application to high-density datasets.

## Motivation
Classical RSSD relies on full pairwise distance computations and combinatorial optimization, which scale poorly (O(n²)) and become infeasible for modern datasets such as drone imagery or dense EMI surveys.

## Key innovation
Replace global spacing optimization with nearest-neighbor-based approximations that:
- Maintain spatial dispersion of calibration sites  
- Preserve representativeness in PCA-transformed sensor space  
- Reduce computational complexity from O(n²) to approximately O(n log n)

## Validation framework
- Compare classical RSSD vs NN-RSSD using:
  - Residual spatial diagnostics
  - Predictive performance (RMSE, R²)
  - Spatial representativeness metrics
  - Computational efficiency scaling

## Outcome
A scalable ESAP-RSSD implementation that extends directed sampling to modern datasets.

---

# Paper 2: Version 3.0 — Modern ESAP-Calibrate (Python Rebuild)

## Core contribution
A complete reimplementation of ESAP-Calibrate in Python with modern statistical learning and uncertainty quantification.

## Motivation
The current ESAP-Calibrate framework relies on manual model selection using PRESS statistics and lacks modern uncertainty quantification.

## Key innovation
Rebuild calibration as a modular framework supporting:

### 1) Modern predictive models
- Regularized regression
- Tree-based models
- Semi-parametric models

### 2) Uncertainty quantification
- Conformal prediction
- Bootstrap methods
- Optional Bayesian approaches

### 3) Model evaluation
- Cross-validation
- Proper scoring rules
- Coverage diagnostics

## Outcome
A fully modern, extensible calibration engine aligned with current statistical practice.

---

# Paper 3: Version 4.0 — Generalized ESAP for Multi-Sensor Spatial Proxies

## Core contribution
Extend ESAP beyond EMI to a general multi-sensor directed sampling framework.

## Motivation
ESAP is fundamentally a sensor-directed sampling framework, not limited to salinity.

## Key innovation
Generalize inputs to include:
- Drone-derived indices
- Terrain attributes
- Multi-sensor fused covariates

## Methodological changes
- Feature extraction across heterogeneous sensors  
- RSSD in generalized feature space  
- Calibration using Version 3.0 framework  

## Outcome
Demonstration that ESAP can reduce sampling burden while maintaining predictive accuracy across sensing modalities.

---

# Paper 4: Version 5.0 — ESAP for Adaptive Sensing and Sensor Network Design

## Core contribution
Extend ESAP from one-time sampling design to optimal sensor network design and adaptive monitoring.

## Motivation
Modern agriculture requires continuous monitoring and cost-efficient sensor placement.

## Key innovation
Use ESAP to:
- Determine optimal fixed sensor placement  
- Enable adaptive sampling over time  
- Integrate with IoT and edge computing  

## Conceptual shift
From:
“Where should I sample today?”

To:
“Where should I place sensors to continuously represent the field over time?”

## Outcome
A framework for cost-efficient, data-driven agricultural sensing systems.

---

# Advisor-Facing Summary

This work proposes a four-stage modernization of ESAP:

1) Scalable ESAP-RSSD for high-density data  
2) Modern calibration framework with uncertainty quantification  
3) Generalization to multi-sensor spatial data  
4) Extension to sensor networks and adaptive monitoring  

Together, these contributions transform ESAP into a general framework for directed sampling, spatial prediction, and sensor optimization in modern agricultural systems.
