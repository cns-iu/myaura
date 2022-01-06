shopt -s expand_aliases

# Load environment
source env.sh
source ../db-config.sh
source ${MAP4SCI_HOME}/.env/bin/activate

# Check required configuration
_=${MAP4SCI_HOME:?"MAP4SCI_HOME Not Set!"}

DATASETS_HOME=${MAP4SCI_HOME}/data-processor/datasets/myaura

# Create directories
mkdir -p "${DATASETS_HOME}"
