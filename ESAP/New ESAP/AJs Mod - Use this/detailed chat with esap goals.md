# 🔍 Project Synopsis: Scaling ESAP for Modern High-Density Sensor Data

## 📌 Background

We are working with an implementation of the **ESAP (Electrical Conductivity Sampling Assessment Program)** / **Spatial Response Surface (SRS)** methodology described by Lesch (2005), which is widely used for selecting optimal soil sampling locations based on sensor data (e.g., EM38).

The core idea of ESAP/SRS is to:
1. Transform sensor data using **PCA** to reduce dimensionality.
2. Define an idealized **response surface design** in PCA space.
3. Select field sampling locations that:
   - Match these PCA targets.
   - Are **maximally spatially distributed** to ensure statistical independence.

---

## 🚨 Problem: ESAP Does Not Scale to Modern Data

The traditional ESAP implementation relies heavily on **full pairwise distance calculations**:

- Uses operations like:
  - `distance_matrix()`
  - `cdist()`
- Computes distances between **all points and all other points**.

### ❗ Computational Implications:
- **Memory complexity:** O(n²)
- **Time complexity:** O(n²)

This becomes prohibitive for modern datasets:
- Drone imagery (10,000–1,000,000+ pixels)
- High-resolution proximal sensors
- Dense EM38 surveys

### 🔴 Result:
- Crashes due to RAM limits
- Extremely slow runtimes
- Not feasible for real-world high-resolution applications

---

## 🎯 Why This Matters

Modern agricultural and environmental monitoring increasingly rely on:
- **Drone-based multispectral imagery (NDVI, NDRE, etc.)**
- **High-density proximal sensing (EM38, Veris, etc.)**
- **Edge-of-field and watershed-scale monitoring**

These datasets are:
- Dense
- Spatially structured
- Information-rich

➡️ But **current ESAP implementations cannot handle them efficiently**, limiting their practical use.

---

## 💡 Proposed Solution: Nearest-Neighbor (NN) Approximation

We are replacing full pairwise distance computations with **nearest-neighbor methods** using structures like:

- `KDTree`
- `BallTree`

### ✅ Benefits:
- **Memory:** O(n log n) instead of O(n²)
- **Speed:** Dramatically faster queries
- **Scalable:** Works with 100k–1M+ points

---

## ⚖️ Key Question

Does replacing full pairwise distance optimization with **nearest-neighbor-based spacing**:

> ❓ Change the methodology?  
> ❓ Or simply improve performance?

---

## 🧠 Working Hypothesis

Nearest-neighbor methods can approximate ESAP’s spatial optimization **without loss of validity**, under reasonable assumptions:

### Assumptions:
1. **Data are uniformly or systematically spaced**
   - Drone pixels (gridded)
   - EM38 transects (structured)

2. **Spatial correlation is short-range**
   - Soil and vegetation properties often decorrelate within ~30–60 m

3. **Residuals are locally structured**
   - PCA + regression captures global trends

4. **PCA space is well-behaved**
   - Continuous, convex, and sufficiently sampled

➡️ Under these conditions:
- **Local spacing constraints ≈ global spacing optimization**
- Nearest-neighbor distance becomes a proxy for full pairwise separation

---

## 📏 Critical Challenge: Choosing Optimal NN Distance

Instead of arbitrarily choosing a spacing threshold (e.g., 30–60 m), we want to **estimate the optimal nearest-neighbor distance (dₙₙ)**.

### Candidate Methods:

#### 1. Empirical Optimization
- Sweep NN distances (20–100 m)
- Evaluate:
  - Model performance (R², RMSE)
  - Residual spatial autocorrelation (Moran’s I)
- Select threshold where:
  - Moran’s I ≈ 0
  - Performance stabilizes

#### 2. Variogram-Based Approach
- Fit variogram to residuals
- Use ~95% of spatial range as NN distance

#### 3. Heuristic (Low-Memory)
- Analyze local variance across k-nearest neighbors
- Choose distance where variance stabilizes

#### 4. Hybrid Validation
- Compare NN-based sampling vs. full ESAP on subset:
  - geoMSD (spatial spread)
  - Moran’s I (independence)
  - Prediction accuracy

---

## 🧪 Goal of Next Steps

We want to:

1. Implement **NN-based sampling** in place of full pairwise distance methods.
2. Determine the **optimal NN distance** using one or more strategies above.
3. Validate that:
   - Spatial independence is preserved
   - Model performance is unchanged
4. Achieve:
   - **Massive reductions in RAM usage**
   - **Scalable performance for large datasets**

---

## ✅ End Goal

Create a **modernized ESAP workflow** that:
- Maintains scientific validity
- Works efficiently on large datasets (drone, EM38, etc.)
- Enables practical field deployment at scale

---

## 🔧 What I Need Help With Next

- Implementing NN-based sampling logic
- Building functions to estimate optimal NN distance
- Validating NN vs. full pairwise methods
- Ensuring statistical assumptions remain satisfied