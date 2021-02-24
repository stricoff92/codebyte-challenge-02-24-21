
### Setup
1. Setup python environment using python 3.6.X or better
2. Install dependancies: `$ pip install -r requirements.txt`
3. Create applocals.py file: `patientemr/patientemr/applocals.py`
4. Add `SECRET_KEY` variable to `applocals.py`. To generate a new secret key run this command `$ python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`

### Run Unit Tests
```bash
$ ./manage.py test
```
