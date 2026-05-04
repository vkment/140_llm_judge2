#!/bin/bash
#SBATCH -o /lnet/aic/personal/kment/py/log/%x-%j.out
#SBATCH -e /lnet/aic/personal/kment/py/log/%x-%j.err

source /lnet/aic/personal/kment/pyenv/140env/bin/activate
cd /lnet/aic/personal/kment/py
python run_judge71.py
