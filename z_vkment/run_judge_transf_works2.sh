#!/bin/bash
#SBATCH -o /lnet/aic/personal/kment/py/log/%x-%j.out
#SBATCH -e /lnet/aic/personal/kment/py/log/%x-%j.err

source /lnet/aic/personal/kment/pyenv/140envb/bin/activate
cd /lnet/aic/personal/kment/py
python run_judge_transf_works2.py
