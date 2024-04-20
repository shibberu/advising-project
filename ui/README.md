test site on http://137.112.104.31:5001/
prod site on http://137.112.104.31:5000/

## Do this the first time to set up environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

## How to run test version
bash run-test.sh

## How to run production version (only do this if you are sure!)
bash run-prod.sh