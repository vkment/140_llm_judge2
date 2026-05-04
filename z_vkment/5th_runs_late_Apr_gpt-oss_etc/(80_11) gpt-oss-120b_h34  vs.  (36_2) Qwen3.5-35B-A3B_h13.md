#### (80_11) gpt-oss-120b_h34  vs.  (36_2) Qwen3.5-35B-A3B_h13 


| criterion                | locale   | acc_eq (80_11) | acc_eq (36_2) | diff    |
| ------------------------ | -------- | -------------- | -------------- | ------- |
|                          |          | gpt-oss-120b   | Qwen3.5-35B    |         |
| ------------------------ | -------- | -------------- | -------------- | ------- |
| instruction_following    | ALL      | 0.586          | 0.559          | 0.028   |
| naturalness              | ALL      | 0.525          | 0.528          | -0.003  |
| coherence                | ALL      | 0.533          | 0.548          | -0.015  |
| -                        | -        | -              | -              | -       |
| instruction_following    | ar_EG    | 0.643          | 0.634          | 0.010   |
| instruction_following    | bn_BD    | 0.508          | 0.474          | 0.034   |
| instruction_following    | cs_CZ    | 0.503          | 0.493          | 0.010   |
| instruction_following    | de_DE    | 0.527          | 0.520          | 0.007   |
| instruction_following    | en_US    | 0.734          | 0.621          | 0.113   |
| instruction_following    | hi_IN    | 0.638          | 0.615          | 0.023   |
| instruction_following    | id_ID    | 0.572          | 0.549          | 0.022   |
| instruction_following    | ja_JP    | 0.479          | 0.493          | -0.014  |
| instruction_following    | ru_RU    | 0.640          | 0.615          | 0.025   |
| instruction_following    | zh_CN    | 0.620          | 0.574          | 0.045   |
| -                        | -        | -              | -              | -       |
| naturalness              | ar_EG    | 0.426          | 0.432          | -0.006  |
| naturalness              | bn_BD    | 0.524          | 0.534          | -0.010  |
| naturalness              | cs_CZ    | 0.543          | 0.532          | 0.012   |
| naturalness              | de_DE    | 0.457          | 0.461          | -0.004  |
| naturalness              | en_US    | 0.623          | 0.589          | 0.034   |
| naturalness              | hi_IN    | 0.550          | 0.549          | 0.001   |
| naturalness              | id_ID    | 0.474          | 0.486          | -0.011  |
| naturalness              | ja_JP    | 0.523          | 0.534          | -0.011  |
| naturalness              | ru_RU    | 0.506          | 0.548          | -0.042  |
| naturalness              | zh_CN    | 0.626          | 0.620          | 0.006   |
| -                        | -        | -              | -              | -       |
| coherence                | ar_EG    | 0.606          | 0.655          | -0.049  |
| coherence                | bn_BD    | 0.509          | 0.500          | 0.009   |
| coherence                | cs_CZ    | 0.484          | 0.508          | -0.024  |
| coherence                | de_DE    | 0.507          | 0.497          | 0.010   |
| coherence                | en_US    | 0.536          | 0.526          | 0.010   |
| coherence                | hi_IN    | 0.570          | 0.601          | -0.031  |
| coherence                | id_ID    | 0.475          | 0.496          | -0.021  |
| coherence                | ja_JP    | 0.528          | 0.542          | -0.013  |
| coherence                | ru_RU    | 0.531          | 0.575          | -0.044  |
| coherence                | zh_CN    | 0.580          | 0.579          | 0.002   |