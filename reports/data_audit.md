# Data audit (M0)

Source: CGMacros 1.0.0

## Files
- Participant files found: **45** (PRD says 45)
- bio.csv rows: 45
- Participants without bio row: none
- bio rows without file: none

## Column sets (raw headers)
- 1 files: `['Unnamed: 0', 'Timestamp', 'Libre GL', 'Dexcom GL', 'HR', 'Calories (Activity)', 'METs', 'Meal Type', 'Calories', 'Carbs', 'Protein', 'Fat', 'Fiber', 'Amount Consumed ', 'Image path']`
- 6 files: `['Unnamed: 0', 'Timestamp', 'Libre GL', 'Dexcom GL', 'HR', 'Calories (Activity)', 'METs', 'Meal Type', 'Calories', 'Carbs', 'Protein', 'Fat', 'Fiber', 'Amount Consumed', 'Image path']`
- 1 files: `['Unnamed: 0', 'Timestamp', 'Dexcom GL', 'Libre GL', 'HR', 'Calories (Activity)', 'METs', 'Meal Type', 'Calories', 'Carbs', 'Protein', 'Fat', 'Fiber', 'Amount Consumed', 'Image path']`
- 1 files: `['Timestamp', 'Libre GL', 'Dexcom GL', 'HR', 'Steps', 'METs', 'Meal Type', 'RecordIndex', 'Calories', 'Carbs', 'Protein', 'Fat', 'Fiber', 'Amount Consumed', 'Image path']`
- 22 files: `['Timestamp', 'Libre GL', 'Dexcom GL', 'HR', 'Calories (Activity)', 'METs', 'Meal Type', 'Calories', 'Carbs', 'Protein', 'Fat', 'Fiber', 'Amount Consumed', 'Image path']`
- 10 files: `['Timestamp', 'Libre GL', 'Dexcom GL', 'HR', 'Calories (Activity)', 'Intensity', 'Meal Type', 'Calories', 'Carbs', 'Protein', 'Fat', 'Fiber', 'Amount Consumed', 'Image path']`
- 1 files: `['Timestamp', 'Libre GL', 'Dexcom GL', 'HR', 'Calories (Activity)', 'METs', 'Meal Type', 'Calories', 'Carbs', 'Protein', 'Fat', 'Fiber', 'Sugar', 'Amount Consumed', 'Image path']`
- 2 files: `['Timestamp', 'Libre GL', 'Dexcom GL', 'HR', 'Calories (Activity)', 'METs', 'Meal Type', 'Calories', 'Carbs', 'Protein', 'Fat', 'Fiber', 'Image path']`
- 1 files: `['Unnamed: 0', 'Timestamp', 'Libre GL', 'Dexcom GL', 'HR', 'Calories (Activity)', 'Intensity', 'Meal Type', 'Calories', 'Carbs', 'Protein', 'Fat', 'Fiber', 'Amount Consumed', 'Image path']`

## Counts per diagnosis group (derived from HbA1c)
| group       |   participants |
|:------------|---------------:|
| healthy     |             15 |
| prediabetes |             16 |
| type2       |             14 |

## Sensor cadence (first 5 participants)
- CGMacros-001: Dexcom rows every 1 min; value changes every 1 min (median); Libre rows every 1 min; value changes every 1 min (median)
- CGMacros-002: Dexcom rows every 1 min; value changes every 1 min (median); Libre rows every 1 min; value changes every 1 min (median)
- CGMacros-003: Dexcom rows every 1 min; value changes every 1 min (median); Libre rows every 1 min; value changes every 1 min (median)
- CGMacros-004: Dexcom rows every 1 min; value changes every 1 min (median); Libre rows every 1 min; value changes every 1 min (median)
- CGMacros-005: Dexcom rows every 1 min; value changes every 1 min (median); Libre rows every 1 min; value changes every 1 min (median)

## Per-participant summary
| pid          | group       |   rows |     days |   dexcom_nonnull |   grid_valid |   interp |   oor |   hr_valid |   meals | meal_types                           |
|:-------------|:------------|-------:|---------:|-----------------:|-------------:|---------:|------:|-----------:|--------:|:-------------------------------------|
| CGMacros-001 | healthy     |  14730 | 10.2285  |            0.968 |        0.969 |        0 |     0 |      0.994 |      43 | Breakfast,Dinner,Lunch,Snacks        |
| CGMacros-002 | healthy     |  17025 | 11.8222  |            0.803 |        0.803 |        0 |     0 |      0.839 |      37 | Breakfast,Dinner,Lunch,Snacks        |
| CGMacros-003 | type2       |  14565 | 10.1243  |            0.979 |        0.979 |        0 |     0 |      0.995 |      35 | Breakfast,Dinner,Lunch,Snacks        |
| CGMacros-004 | healthy     |  14275 |  9.9125  |            1     |        1     |        0 |     0 |      0.998 |      62 | Breakfast,Dinner,Lunch,Snacks        |
| CGMacros-005 | type2       |  14460 | 10.041   |            0.987 |        0.987 |        0 |     0 |      0.988 |      46 | Breakfast,Lunch,dinner,snack         |
| CGMacros-006 | healthy     |  14460 | 10.041   |            0.987 |        0.987 |        0 |     0 |      0.992 |      38 | breakfast,dinner,lunch,snack         |
| CGMacros-007 | prediabetes |   5655 |  7.22847 |            0.997 |        0.981 |      402 |     0 |      0.786 |      17 | breakfast,dinner,lunch,snack         |
| CGMacros-008 | prediabetes |  14760 | 10.2493  |            0.963 |        0.967 |        0 |     0 |      0.978 |      30 | breakfast,dinner,lunch               |
| CGMacros-009 | prediabetes |  14370 |  9.97847 |            0.99  |        0.991 |        0 |     0 |      0.986 |      41 | breakfast,dinner,lunch,snack,snack 1 |
| CGMacros-010 | prediabetes |  16155 | 11.2181  |            0.884 |        0.883 |        0 |     0 |      0.938 |      45 | breakfast,dinner,lunch,snack         |
| CGMacros-011 | prediabetes |  14805 | 10.2806  |            0.964 |        0.965 |        0 |     0 |      0.99  |      39 | breakfast,dinner,lunch,snack         |
| CGMacros-012 | type2       |  14655 | 10.1868  |            0.974 |        0.973 |        0 |     0 |      0.915 |      33 | Dinner,breakfast,dinner,lunch,snack  |
| CGMacros-013 | prediabetes |  15840 | 10.9993  |            0.901 |        0.901 |        0 |     0 |      0.96  |      39 | Breakfast,Lunch,dinner,snack         |
| CGMacros-014 | type2       |  17250 | 11.9785  |            0.828 |        0.828 |        0 |     0 |      0.879 |      40 | Breakfast,Lunch,dinner,snack         |
| CGMacros-015 | healthy     |  16875 | 11.9681  |            0.842 |        0.828 |        0 |     0 |      0.874 |      52 | Breakfast,Lunch,dinner,snack         |
| CGMacros-016 | prediabetes |  16290 | 11.3118  |            0.876 |        0.876 |        0 |     0 |      0.935 |      28 | Breakfast,Lunch,dinner,snack         |
| CGMacros-017 | healthy     |  16185 | 11.2389  |            0.88  |        0.882 |        3 |     0 |      0.843 |      48 | Breakfast,Lunch,dinner,snack         |
| CGMacros-018 | healthy     |  14085 | 19.1535  |            0.989 |        0.505 |        0 |     0 |      0.508 |      39 | Breakfast,Dinner,Lunch,Snack,snack   |
| CGMacros-019 | healthy     |  14430 | 10.0306  |            0.988 |        0.988 |        0 |     0 |      0.98  |      48 | Breakfast,Lunch,dinner,snack         |
| CGMacros-020 | prediabetes |  16260 | 11.291   |            0.878 |        0.878 |        0 |     0 |      0.884 |      41 | Breakfast,Lunch,dinner,snack         |
| CGMacros-021 | healthy     |  16125 | 11.1972  |            0.885 |        0.885 |        0 |     0 |      0.938 |      39 | Breakfast,Lunch,dinner,snack         |
| CGMacros-022 | prediabetes |  17625 | 12.2389  |            0.81  |        0.81  |        0 |     0 |      0.825 |      42 | Breakfast,Lunch,dinner,snack         |
| CGMacros-023 | prediabetes |  16185 | 11.2389  |            0.881 |        0.882 |        0 |     0 |      0.935 |      42 | Breakfast,Lunch,dinner,snack         |
| CGMacros-026 | prediabetes |  16320 | 11.3326  |            0.847 |        0.848 |        0 |     0 |      0.933 |      36 | Breakfast,Lunch,dinner,snack         |
| CGMacros-027 | healthy     |  14535 | 10.0931  |            0.978 |        0.982 |        9 |     0 |      0.998 |      36 | breakfast,dinner,lunch,snack         |
| CGMacros-028 | type2       |  18735 | 13.0097  |            0.76  |        0.762 |        5 |     0 |      0.764 |      34 | breakfast,dinner,lunch,snack         |
| CGMacros-029 | prediabetes |  17730 | 12.3118  |            0.805 |        0.805 |        0 |     0 |      0.851 |      30 | breakfast,dinner,lunch               |
| CGMacros-030 | type2       |  15465 | 10.7389  |            0.919 |        0.923 |        9 |     0 |      0.803 |      28 | breakfast,dinner,lunch               |
| CGMacros-031 | healthy     |  13725 |  9.53056 |            0.996 |        0.996 |        0 |     0 |      0.988 |      54 | breakfast,dinner,lunch,snack         |
| CGMacros-032 | healthy     |  13785 |  9.57222 |            0.991 |        0.992 |        0 |     0 |      0.481 |      20 | breakfast,dinner,lunch               |
| CGMacros-033 | healthy     |  15840 | 11.0097  |            0.897 |        0.9   |        4 |     0 |      0.689 |      33 | breakfast,dinner,lunch,snack         |
| CGMacros-034 | healthy     |  14700 | 10.2076  |            0.971 |        0.971 |        0 |     0 |      0.548 |      49 | breakfast,dinner,lunch,snack         |
| CGMacros-035 | type2       |  14400 |  9.99931 |            0.991 |        0.991 |        0 |     0 |      0.839 |      27 | breakfast,dinner,lunch               |
| CGMacros-036 | type2       |  17115 | 11.8847  |            0.834 |        0.834 |        0 |     0 |      0.843 |      30 | breakfast,dinner,lunch               |
| CGMacros-038 | type2       |  14505 | 10.0722  |            0.984 |        0.984 |        0 |     0 |      0.991 |      40 | breakfast,dinner,lunch,snack         |
| CGMacros-039 | type2       |  17205 | 11.9472  |            0.83  |        0.83  |        0 |     0 |      0.838 |      34 | breakfast,dinner,lunch,snack         |
| CGMacros-041 | prediabetes |  14310 |  9.93681 |            0.995 |        0.995 |        0 |     0 |      0.689 |      48 | breakfast,dinner,lunch,snack         |
| CGMacros-042 | type2       |  14520 | 10.0826  |            0.983 |        0.983 |        0 |     0 |      0.917 |      22 | breakfast,dinner,lunch,snack         |
| CGMacros-043 | prediabetes |  14520 | 10.0931  |            0.982 |        0.982 |        0 |     0 |      0.967 |      64 | breakfast,dinner,lunch,snack         |
| CGMacros-044 | prediabetes |  14535 | 10.0931  |            0.979 |        0.982 |        6 |     0 |      0.844 |      43 | breakfast,dinner,lunch,snack         |
| CGMacros-045 | prediabetes |  15570 | 10.8118  |            0.878 |        0.878 |        0 |     0 |      0.938 |      32 | breakfast,dinner,lunch,snack         |
| CGMacros-046 | type2       |  14655 | 10.1972  |            0.972 |        0.972 |        0 |     0 |      0.93  |      29 | breakfast,dinner,lunch               |
| CGMacros-047 | type2       |  15690 | 10.8951  |            0.907 |        0.91  |        2 |     0 |      0.919 |      29 | breakfast,dinner,lunch               |
| CGMacros-048 | healthy     |  17340 | 12.0514  |            0.822 |        0.823 |        0 |     0 |      0.83  |      36 | breakfast,dinner,lunch,snack         |
| CGMacros-049 | type2       |  15315 | 10.6347  |            0.932 |        0.932 |        0 |     0 |      0.914 |      28 | breakfast,dinner,lunch               |

## Threshold selection rule

Rule: first T in [180, 160, 140] with >= 15 participants having >= 5 post-warm-up episodes AND >= 2% positive eligible windows (120 min horizon).

| T | participants with >=5 episodes | total episodes | eligible windows | positive % | passes |
|---|---|---|---|---|---|
| 180 | 30 | 501 | 86536 | 13.94% | yes |
| 160 | 39 | 693 | 77695 | 21.89% | yes |
| 140 | 42 | 810 | 60732 | 33.69% | yes |

**Chosen T = 180 mg/dL** (frozen in config.yaml).
