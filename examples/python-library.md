<p align="center">
  <h1 align="center">🔢 NumPy</h1>
  <p align="center">
    <strong>The fundamental package for scientific computing with Python</strong>
  </p>
  <p align="center">
    <a href="#-features">Features</a> • 
    <a href="#-installation">Installation</a> • 
    <a href="#-quick-start">Quick Start</a> • 
    <a href="#-documentation">Documentation</a> • 
    <a href="#-contributing">Contributing</a>
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-1.24.0-blue?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/license-BSD-green?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/python-3.8+-yellow?style=flat-square" alt="Python">
  <img src="https://img.shields.io/pypi/pyversions/numpy?style=flat-square" alt="Python Versions">
  <img src="https://img.shields.io/github/stars/numpy/numpy?style=social" alt="Stars">
</p>

---

## ✨ Features

<table>
  <tr>
    <td width="50%">
      <h3>📊 N-dimensional Array</h3>
      <ul>
        <li>Powerful N-dimensional array object</li>
        <li>Broadcasting functions</li>
        <li>Vectorization</li>
      </ul>
    </td>
    <td width="50%">
      <h3>🔢 Mathematical Functions</h3>
      <ul>
        <li>Linear algebra operations</li>
        <li>Fourier transforms</li>
        <li>Random number capabilities</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3>⚡ Performance</h3>
      <ul>
        <li>C-based implementation</li>
        <li>Optimized for speed</li>
        <li>Memory efficient</li>
      </ul>
    </td>
    <td width="50%">
      <h3>🔗 Integration</h3>
      <ul>
        <li>Works with SciPy, Pandas, Matplotlib</li>
        <li>Array interface standard</li>
        <li>FFI friendly</li>
      </ul>
    </td>
  </tr>
</table>

---

## 🚀 Quick Start

### Installation

```bash
pip install numpy
```

### Basic Usage

```python
import numpy as np

# Create array
arr = np.array([1, 2, 3, 4, 5])

# Array operations
print(arr.mean())      # 3.0
print(arr.std())       # 1.4142135623730951
print(arr * 2)         # [2 4 6 8 10]

# 2D array
matrix = np.array([[1, 2, 3], [4, 5, 6]])
print(matrix.shape)    # (2, 3)
```

---

## 📦 Installation

### Requirements

- Python 3.8+
- pip

### Install

```bash
# Stable version
pip install numpy

# Development version
pip install numpy --pre

# From source
git clone https://github.com/numpy/numpy.git
cd numpy
pip install -e .
```

### Conda

```bash
conda install numpy
```

---

## 📖 Documentation

- [Official Documentation](https://numpy.org/doc/)
- [NumPy Reference](https://numpy.org/doc/stable/reference/)
- [NumPy Tutorials](https://numpy.org/doc/stable/user/tutorials.html)
- [API Reference](https://numpy.org/doc/stable/reference/index.html)

---

## 🧪 Examples

### Array Creation

```python
import numpy as np

# From list
arr = np.array([1, 2, 3, 4, 5])

# Zeros
zeros = np.zeros((3, 3))

# Ones
ones = np.ones((2, 4))

# Identity matrix
eye = np.eye(3)

# Random
rand = np.random.rand(3, 3)
```

### Array Operations

```python
import numpy as np

a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

# Element-wise operations
print(a + b)      # [5 7 9]
print(a * b)      # [4 10 18]
print(a ** 2)     # [1 4 9]

# Dot product
print(np.dot(a, b))  # 32
```

### Linear Algebra

```python
import numpy as np

A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

# Matrix multiplication
C = np.dot(A, B)
# or
C = A @ B

# Determinant
det = np.linalg.det(A)

# Inverse
inv = np.linalg.inv(A)

# Eigenvalues
eigenvalues, eigenvectors = np.linalg.eig(A)
```

---

## 📊 Benchmarks

| Operation | NumPy | Python List | Speedup |
|-----------|-------|-------------|---------|
| Array creation | 0.001s | 0.01s | 10x |
| Element-wise ops | 0.002s | 0.05s | 25x |
| Matrix multiply | 0.01s | 0.1s | 10x |

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone repository
git clone https://github.com/numpy/numpy.git
cd numpy

# Install in development mode
pip install -e .[dev]

# Run tests
pytest numpy/tests/
```

---

## 📄 License

NumPy is licensed under the BSD License. See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- Travis E. Oliphant for creating NumPy
- The entire NumPy community for their contributions

---

<p align="center">
  <strong>⭐ If NumPy helps you, please give it a star!</strong>
</p>

<p align="center">
  <a href="https://star-history.com/#numpy/numpy&Date">
    <img src="https://api.star-history.com/svg?repos=numpy/numpy&type=Date" alt="Star History Chart" width="600">
  </a>
</p>
