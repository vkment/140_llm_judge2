#### (75_2) Gemma-4-31B-IT-NVFP4  vs.  (74_2) Gemma-4-31B-IT-NVFP4_h23 

The table compares runs of the same model (Gemma-4-31B-IT-NVFP4) with the default template (anchors only: 7-5-3-1) on the left side and the h23 hybrid template on the right side. It shows that the h23 template helps mostly the **Czech** locale (and **Japanese**), while the remaining locales perform better with the default prompt. In particular, **English** performs significantly better with the original template from the Kocmi study.


| criterion                | locale   | acc_eq (75_2)   | acc_eq (74_2)   | diff    |
| ------------------------ | -------- | --------------- | --------------- | ------- |
|                          |          | quantiz. NVFP4  | quantiz. NVFP4_**h23** |         |
| | | **kocmi** template | hybrid **h23** template | |
| ------------------------ | -------- | --------------- | --------------- | ------- |
| instruction_following    | ALL      | 0.605           | 0.594           | 0.011   |
| naturalness              | ALL      | 0.545           | 0.527           | 0.017   |
| coherence                | ALL      | 0.598           | 0.586           | 0.013   |
| -                        | -        | -               | -               | -       |
| instruction_following    | ar_EG    | 0.660           | 0.639           | 0.021   |
| instruction_following    | bn_BD    | 0.499           | 0.493           | 0.006   |
| instruction_following    | **cs_CZ** | 0.490       | **0.508**       | -0.018   |
| instruction_following    | de_DE    | 0.592           | 0.559           | 0.032   |
| instruction_following    | **en_US** | **0.758**       | 0.735           | 0.023   |
| instruction_following    | hi_IN    | 0.637           | 0.621           | 0.016   |
| instruction_following    | id_ID    | 0.602           | 0.585           | 0.017   |
| instruction_following    | ja_JP    | 0.499           | 0.524           | -0.025   |
| instruction_following    | ru_RU    | 0.650           | 0.631           | 0.019   |
| instruction_following    | zh_CN    | 0.660           | 0.640           | 0.020   |
| -                        | -        | -               | -               | -       |
| naturalness              | ar_EG    | 0.482           | 0.489           | -0.007   |
| naturalness              | bn_BD    | 0.528           | 0.530           | -0.002   |
| naturalness              | **cs_CZ** | 0.529       | **0.538**       | -0.009   |
| naturalness              | de_DE    | 0.489           | 0.442           | 0.047   |
| naturalness              | **en_US** | **0.632**       | 0.598           | 0.034   |
| naturalness              | hi_IN    | 0.581           | 0.501           | 0.080   |
| naturalness              | id_ID    | 0.478           | 0.461           | 0.017   |
| naturalness              | ja_JP    | 0.538           | 0.549           | -0.012   |
| naturalness              | ru_RU    | 0.553           | 0.579           | -0.026   |
| naturalness              | zh_CN    | 0.638           | 0.585           | 0.053   |
| -                        | -        | -               | -               | -       |
| coherence                | ar_EG    | 0.682           | 0.673           | 0.009   |
| coherence                | bn_BD    | 0.500           | 0.511           | -0.011   |
| coherence                | **cs_CZ** | 0.443       | **0.499**       | -0.056   |
| coherence                | de_DE    | 0.624           | 0.588           | 0.036   |
| coherence                | **en_US** | **0.654**       | 0.633           | 0.021   |
| coherence                | hi_IN    | 0.684           | 0.638           | 0.046   |
| coherence                | id_ID    | 0.469           | 0.484           | -0.014   |
| coherence                | ja_JP    | 0.572           | 0.563           | 0.009   |
| coherence                | ru_RU    | 0.660           | 0.614           | 0.046   |
| coherence                | zh_CN    | 0.696           | 0.656           | 0.040   |
