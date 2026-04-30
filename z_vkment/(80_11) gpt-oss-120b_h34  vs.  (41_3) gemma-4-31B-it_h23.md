#### (80_11) gpt-oss-120b_h34  vs.  (41_3) gemma-4-31B-it_h23 


| criterion                | locale   | acc_eq (80_11) | acc_eq (41_3) | diff    |
| ------------------------ | -------- | -------------- | -------------- | ------- |
|                          |          | gpt-oss-120b   | gemma-4-31B    |         |
| ------------------------ | -------- | -------------- | -------------- | ------- |
| instruction_following    | ALL      | 0.586          | 0.591          | -0.005  |
| naturalness              | ALL      | 0.525          | 0.526          | -0.000  |
| coherence                | ALL      | 0.533          | 0.585          | -0.053  |
| -                        | -        | -              | -              | -       |
| instruction_following    | ar_EG    | 0.643          | 0.634          | 0.009   |
| instruction_following    | bn_BD    | 0.508          | 0.497          | 0.011   |
| instruction_following    | cs_CZ    | 0.503          | **0.510**      | -0.007  |
| instruction_following    | de_DE    | 0.527          | 0.557          | -0.030  |
| instruction_following    | en_US    | 0.734          | **0.737**      | -0.003  |
| instruction_following    | hi_IN    | 0.638          | 0.617          | 0.021   |
| instruction_following    | id_ID    | 0.572          | 0.578          | -0.007  |
| instruction_following    | ja_JP    | 0.479          | 0.514          | -0.035  |
| instruction_following    | ru_RU    | 0.640          | 0.622          | 0.018   |
| instruction_following    | zh_CN    | 0.620          | 0.645          | -0.026  |
| -                        | -        | -              | -              | -       |
| naturalness              | ar_EG    | 0.426          | 0.489          | -0.064  |
| naturalness              | bn_BD    | 0.524          | 0.534          | -0.010  |
| naturalness              | cs_CZ    | **0.543**      | **0.540**      | 0.003   |
| naturalness              | de_DE    | 0.457          | 0.440          | 0.017   |
| naturalness              | en_US    | **0.623**      | 0.599          | 0.024   |
| naturalness              | hi_IN    | 0.550          | 0.496          | 0.054   |
| naturalness              | id_ID    | 0.474          | 0.464          | 0.010   |
| naturalness              | ja_JP    | 0.523          | 0.537          | -0.014  |
| naturalness              | ru_RU    | 0.506          | 0.583          | -0.077  |
| naturalness              | zh_CN    | 0.626          | 0.574          | 0.052   |
| -                        | -        | -              | -              | -       |
| coherence                | ar_EG    | 0.606          | 0.675          | -0.069  |
| coherence                | bn_BD    | 0.509          | 0.513          | -0.004  |
| coherence                | cs_CZ    | 0.484          | **0.501**      | -0.017  |
| coherence                | de_DE    | 0.507          | 0.582          | -0.075  |
| coherence                | en_US    | 0.536          | **0.630**      | -0.094  |
| coherence                | hi_IN    | 0.570          | 0.624          | -0.054  |
| coherence                | id_ID    | 0.475          | 0.489          | -0.014  |
| coherence                | ja_JP    | 0.528          | 0.561          | -0.033  |
| coherence                | ru_RU    | 0.531          | 0.617          | -0.086  |
| coherence                | zh_CN    | 0.580          | 0.661          | -0.080  |