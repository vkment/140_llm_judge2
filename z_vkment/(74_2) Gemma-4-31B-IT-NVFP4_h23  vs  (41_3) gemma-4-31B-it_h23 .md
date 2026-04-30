#### (74_2) Gemma-4-31B-IT-NVFP4_h23  vs.  (41_3) gemma-4-31B-it_h23 


| criterion                | locale   | acc_eq (74_2)   | acc_eq (41_3)   | diff    |
| ------------------------ | -------- | --------------- | --------------- | ------- |
|                          |          | quantiz. NVFP4  | BF16            |         |
| ------------------------ | -------- | --------------- | --------------- | ------- |
| instruction_following    | ALL      | 0.594           | 0.591           | 0.002   |
| naturalness              | ALL      | 0.527           | 0.526           | 0.002   |
| coherence                | ALL      | 0.586           | 0.585           | 0.000   |
| -                        | -        | -               | -               | -       |
| instruction_following    | ar_EG    | 0.639           | 0.634           | 0.004   |
| instruction_following    | bn_BD    | 0.493           | 0.497           | -0.004  |
| instruction_following    | cs_CZ    | **0.508**       | 0.510           | -0.002  |
| instruction_following    | de_DE    | 0.559           | 0.557           | 0.003   |
| instruction_following    | en_US    | 0.735           | 0.737           | -0.002  |
| instruction_following    | hi_IN    | 0.621           | 0.617           | 0.004   |
| instruction_following    | id_ID    | 0.585           | 0.578           | 0.006   |
| instruction_following    | ja_JP    | 0.524           | 0.514           | 0.010   |
| instruction_following    | ru_RU    | 0.631           | 0.622           | 0.009   |
| instruction_following    | zh_CN    | 0.640           | 0.645           | -0.006  |
| -                        | -        | -               | -               | -       |
| naturalness              | ar_EG    | 0.489           | 0.489           | 0.000   |
| naturalness              | bn_BD    | 0.530           | 0.534           | -0.004  |
| naturalness              | cs_CZ    | **0.538**       | 0.540           | -0.002  |
| naturalness              | de_DE    | 0.442           | 0.440           | 0.002   |
| naturalness              | en_US    | 0.598           | 0.599           | -0.001  |
| naturalness              | hi_IN    | 0.501           | 0.496           | 0.006   |
| naturalness              | id_ID    | 0.461           | 0.464           | -0.003  |
| naturalness              | ja_JP    | 0.549           | 0.537           | 0.012   |
| naturalness              | ru_RU    | 0.579           | 0.583           | -0.004  |
| naturalness              | zh_CN    | 0.585           | 0.574           | 0.011   |
| -                        | -        | -               | -               | -       |
| coherence                | ar_EG    | 0.673           | 0.675           | -0.002  |
| coherence                | bn_BD    | 0.511           | 0.513           | -0.002  |
| coherence                | cs_CZ    | **0.499**       | 0.501           | -0.002  |
| coherence                | de_DE    | 0.588           | 0.582           | 0.006   |
| coherence                | en_US    | 0.633           | 0.630           | 0.003   |
| coherence                | hi_IN    | 0.638           | 0.624           | 0.014   |
| coherence                | id_ID    | 0.484           | 0.489           | -0.005  |
| coherence                | ja_JP    | 0.563           | 0.561           | 0.001   |
| coherence                | ru_RU    | 0.614           | 0.617           | -0.003  |
| coherence                | zh_CN    | 0.656           | 0.661           | -0.005  |