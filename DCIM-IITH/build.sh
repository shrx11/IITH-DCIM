cd "$(dirname "$0")"
VIRTUALENV="$(pwd -P)/venv"
PYTHON="${PYTHON:-python3}"

COMMAND="${PYTHON} -c 'import sys; exit(1 if sys.version_info < (3, 8) else 0)'"
PYTHON_VERSION=$(eval "${PYTHON} -V")
eval $COMMAND
echo "Using ${PYTHON_VERSION}"

if [ -d "$VIRTUALENV" ]; then
  COMMAND="rm -rf ${VIRTUALENV}"
  echo "Removing old virtual environment..."
  eval $COMMAND
else
  WARN_MISSING_VENV=1
fi

COMMAND="${PYTHON} -m venv ${VIRTUALENV}"
echo "Creating a new virtual environment at ${VIRTUALENV}..."
eval $COMMAND || {
  echo "--------------------------------------------------------------------"
  echo "ERROR: Failed to create the virtual environment. Check that you have"
  echo "the required system packages installed and the following path is"
  echo "writable: ${VIRTUALENV}"
  echo "--------------------------------------------------------------------"
  exit 1
}

source "${VIRTUALENV}/bin/activate"

# Upgrade pip
COMMAND="pip install --upgrade pip"
echo "Updating pip ($COMMAND)..."
eval $COMMAND || exit 1
pip -V

# Install necessary system packages
COMMAND="pip install wheel"
echo "Installing Python system packages ($COMMAND)..."
eval $COMMAND || exit 1

# Install required Python packages
COMMAND="pip install -r requirements.txt"
echo "Installing core dependencies ($COMMAND)..."
eval $COMMAND || exit 1

# Install optional packages (if any)
if [ -s "local_requirements.txt" ]; then
  COMMAND="pip install -r local_requirements.txt"
  echo "Installing local dependencies ($COMMAND)..."
  eval $COMMAND || exit 1
elif [ -f "local_requirements.txt" ]; then
  echo "Skipping local dependencies (local_requirements.txt is empty)"
else
  echo "Skipping local dependencies (local_requirements.txt not found)"
fi

# # Apply any database migrations
# COMMAND="python3 netbox/manage.py migrate"
# echo "Applying database migrations ($COMMAND)..."
# eval $COMMAND || exit 1

# Trace any missing cable paths (not typically needed)
COMMAND="python3 code/manage.py trace_paths --no-input"
echo "Checking for missing cable paths ($COMMAND)..."
eval $COMMAND || exit 1

# # Build the local documentation
# COMMAND="mkdocs build"
# echo "Building documentation ($COMMAND)..."
# eval $COMMAND || exit 1

# Collect static files
COMMAND="python3 code/manage.py collectstatic --no-input"
echo "Collecting static files ($COMMAND)..."
eval $COMMAND || exit 1

# Delete any stale content types
COMMAND="python3 code/manage.py remove_stale_contenttypes --no-input"
echo "Removing stale content types ($COMMAND)..."
eval $COMMAND || exit 1

# Rebuild the search cache (lazily)
COMMAND="python3 code/manage.py reindex --lazy"
echo "Rebuilding search cache ($COMMAND)..."
eval $COMMAND || exit 1

# Delete any expired user sessions
COMMAND="python3 code/manage.py clearsessions"
echo "Removing expired user sessions ($COMMAND)..."
eval $COMMAND || exit 1

# Clear the cache
COMMAND="python3 code/manage.py clearcache"
echo "Clearing the cache ($COMMAND)..."
eval $COMMAND || exit 1

echo "Upgrade complete!"