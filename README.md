# ACEest Fitness and Gym - CI/CD DevOps Project

## Overview
This repository implements an automated CI/CD pipeline for the ACEest Fitness and Gym application, tracking iterative updates from version 1.0 to 3.2.4.

## Pipeline Architecture
- **Trigger**: Automated GitHub Actions workflow on `push` and `tags`.
- **Quality Gates**: Automated dependency installation and `pytest` test suite execution.
- **Containerization**: Automated Docker image building.

## Versioning Strategy
Releases are tagged sequentially using Git tags (`v1.0`, `v1.1`, ..., `v3.2.4`) to maintain a real-world audit trail of script iterations.
