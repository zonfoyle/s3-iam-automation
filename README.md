# S3 + IAM Automation 🚀

This project automates secure AWS S3 storage and IAM access control using Python and boto3.

## 📌 Problem Statement

Manually creating cloud storage resources and configuring IAM permissions can be repetitive, error-prone, and difficult to scale consistently.

This project solves that by automating S3 bucket provisioning, file uploads, IAM user creation, and scoped access policy assignment using Python.

---

## 📌 Overview

This system provisions cloud resources programmatically, including:

- S3 bucket creation
- File upload to S3
- S3 object listing
- IAM user creation
- Custom IAM policy generation
- Policy attachment for controlled access

The script is designed to be **idempotent**, meaning it safely reuses existing resources instead of creating duplicates.

---

## 🧱 Architecture

config.yaml  
↓  
main.py  
↓  
utils.py  
↓  
AWS (S3 + IAM)

---

## 🧠 Design Decisions

- Used **boto3** to gain direct programmatic control over AWS resources and strengthen AWS SDK automation skills.
- Used **S3** as the storage layer because it is a foundational AWS service used heavily in real-world cloud environments.
- Used **IAM policies scoped to a single bucket** to follow least-privilege principles rather than granting broad S3 permissions.
- Added **idempotent logic** so rerunning the script safely reuses existing resources.

---

## ⚙️ Features

- Automated S3 bucket provisioning
- File upload and object listing
- IAM user creation
- Scoped S3 access policy (least privilege)
- Idempotent resource handling

---

## 🛠️ Tech Stack

- Python
- boto3
- PyYAML
- AWS S3
- AWS IAM

---

## 🚀 How to Run

1. Configure AWS credentials:

```bash
aws configure