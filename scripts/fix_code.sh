#!/bin/bash
set -e

# Chemin vers le projet
PROJECT_DIR="$(dirname "$(realpath "$0")")/../back"

echo "==> Vérification et correction automatique du code Python dans $PROJECT_DIR"

# 1️⃣ Corriger le formatage avec autopep8
echo "-> Formatage autopep8..."
poetry run autopep8 --in-place --aggressive --aggressive $(find "$PROJECT_DIR" -name "*.py")

# 2️⃣ Trier et organiser les imports avec isort
echo "-> Organisation des imports avec isort..."
poetry run isort $(find "$PROJECT_DIR" -name "*.py")

# 3️⃣ Vérifier avec flake8 pour voir les imports/variables inutilisés
echo "-> Vérification des imports et variables inutilisées (F401/F841)..."
poetry run flake8 "$PROJECT_DIR" --select=F
black
echo "==> Terminé. Les erreurs F401/F841 doivent être corrigées manuellement."
