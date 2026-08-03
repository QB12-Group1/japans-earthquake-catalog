# Comparative Analysis of Earthquake Catalogs and Seismic Activity in Japan

**Project:** Japan Earthquake Catalog Analysis
**Analysis Period:** Based on the provided earthquake dataset and generated visualizations

---

## Executive Summary

This report presents a comparative analysis of earthquake data collected from four different catalogs:

- USGS (United States Geological Survey)
- EMSC (European-Mediterranean Seismological Centre)
- GEOFON
- Side Dataset (DATASET)

The objectives of this analysis are to:

- evaluate the completeness of each source,
- investigate the relationship between earthquake magnitude and depth,
- compare the detection capability of different catalogs,
- identify potentially hazardous earthquakes, and
- provide recommendations for combining multiple data sources to improve data quality.

The analysis is based on the following visualizations:

- Magnitude distribution by source
- Magnitude distribution by depth group
- Earthquake magnitude over time
- Earthquake frequency by hour
- Earthquake frequency by weekday
- Earthquake count by date

Severity throughout this report follows the project’s official classification defined during the SQL cleaning stage:

- **Weak** = magnitude < 4
- **Moderate** = 4 ≤ magnitude ≤ 6
- **Strong** = magnitude > 6

---

## 1. Do All Sources Detect Small Earthquakes?

### Analysis

The histogram of earthquake magnitudes clearly shows that the four catalogs have significantly different detection capabilities.

### EMSC

EMSC contains the widest magnitude range, extending from approximately **M2.1 to M5.5**.

A considerable proportion of earthquakes are concentrated between **Magnitude 3.0 and 4.2**, indicating that this catalog is highly sensitive to low-magnitude events.

The large number of small earthquakes suggests that EMSC prioritizes recording local and regional seismic activity.

**Strengths:**

- Excellent coverage of weak earthquakes
- Large number of recorded events
- High sensitivity to low-magnitude seismicity

### USGS

USGS records are mainly concentrated between **Magnitude 4.0 and 5.2**.

Very few earthquakes below **Magnitude 3** are present.

However, USGS contains several larger earthquakes above **Magnitude 5.5**, including the strongest event observed in this dataset.

**Strengths:**

- High-quality global catalog
- Excellent coverage of moderate and strong earthquakes
- Reliable parameters for scientific analysis

### GEOFON

GEOFON contains relatively few events.

Most earthquakes have magnitudes greater than **4.5**, indicating that this catalog mainly focuses on moderate and large earthquakes.

The strongest earthquake is also represented in this source.

**Strengths:**

- Accurate monitoring of significant earthquakes
- Useful for validation of major seismic events

### Side Dataset

The additional dataset mainly contains earthquakes between **Magnitude 4.2 and 5.3**.

Small earthquakes are almost completely absent.

This suggests that the dataset is likely filtered or selected for specific analyses rather than representing a complete earthquake catalog.

### Conclusion

The histogram clearly shows that not all catalogs detect small earthquakes equally well.

**EMSC** provides the most comprehensive coverage of weak earthquakes, while **USGS** and **GEOFON** mainly emphasize moderate and large events.

Therefore, relying on a single source would inevitably lead to incomplete earthquake records.

---

## 2. At What Depth Do Strong Earthquakes Usually Occur?

### Analysis

The boxplot compares earthquake magnitude across three depth categories:

- Shallow
- Intermediate
- Deep

### Shallow Earthquakes

The shallow group exhibits the largest variability.

**Characteristics:**

- Median magnitude ≈ **4.0**
- Magnitude range approximately **2.1–6.8**
- Largest observed earthquake ≈ **6.8**
- Highest dispersion among all groups

This indicates that shallow earthquakes include both the weakest and the strongest recorded events.

### Intermediate Earthquakes

**Characteristics:**

- Median magnitude ≈ **4.4**
- Most earthquakes lie between **4.0 and 4.7**
- Moderate variability

Earthquakes in this category tend to have relatively consistent magnitudes.

### Deep Earthquakes

**Characteristics:**

- Median magnitude ≈ **4.0**
- Small variability
- Few earthquakes exceed **Magnitude 5**

Deep earthquakes appear much more uniform and generally do not include the strongest events in the dataset.

### Scientific Interpretation

The largest earthquakes are concentrated within the **shallow depth group**.

This observation is consistent with tectonic theory because shallow earthquakes release seismic energy much closer to Earth’s surface, making them potentially more destructive.

Although deep earthquakes may possess considerable energy, their greater focal depth generally reduces the intensity of surface shaking.

### Conclusion

The strongest earthquakes in this dataset are predominantly **shallow**, which increases their hazard potential.

---

## 3. Ranking the Most Hazardous Earthquakes

Earthquake hazard depends primarily on two parameters:

- High magnitude
- Low focal depth

To ensure scientific accuracy, this ranking is based on the actual `earthquakes` table rather than visual estimation from plots.


### Result

Only **3 earthquakes** in the dataset satisfied the project’s official **Strong + shallow** hazard criteria:

- **Strong:** magnitude > 6
- **Shallow:** depth < 50 km

| Rank | Time | Place / Region | Magnitude | Depth (km) | Source | Hazard Level |
|------|------|----------------|-----------|------------|--------|---------------|
| 1 | 2026-07-28 07:27:14 | Kyushu, Japan / Kyushu | 6.8 | 10 | GEOFON | Extremely High |
| 2 | 2026-07-28 07:27:15 | 2026 Uto, Japan Earthquake / Uto | 6.8 | 10 | USGS | Extremely High |
| 3 | 2026-07-03 04:04:48 | 147 km NNE of Hirara, Japan / Hirara | 6.1 | 10 | USGS | High |

### Interpretation

Only **three records** met the combined condition of being both **strong** and **shallow**. All three earthquakes occurred at a depth of only **10 km**, which significantly increases their potential to generate strong surface shaking.

The first and second records have identical magnitude and depth values and occurred only about **one second apart**. They were reported by **GEOFON** and **USGS**, respectively. This strongly suggests that they represent the **same physical earthquake**, independently recorded by two catalogs: the **2026 Uto/Kyushu earthquake**.

This cross-catalog agreement is important because it:

- increases confidence in the event’s significance,
- confirms the usefulness of multi-source validation, and
- highlights the need for duplicate-event detection when integrating catalogs.

The third-ranked event occurred near **Hirara, Japan**, with a magnitude of **6.1** and a shallow depth of **10 km**. Although smaller than the Uto/Kyushu event, its shallow focal depth still makes it one of the most potentially damaging earthquakes in the dataset.

### Conclusion

The most hazardous earthquakes in the dataset are **shallow strong events**, especially the **M6.8 Uto/Kyushu earthquake**, which appears in two independent catalogs.

---

## 4. Comparison of Large Earthquakes Among Sources

To remain consistent with the project’s official severity classification, **large earthquakes are defined here as Strong events: magnitude > 6**.

This definition matches the `category` column already computed in the database and ensures consistency between the report and the cleaned table.


### USGS

USGS contains the largest number of strong earthquakes in the current analysis.

It also records the maximum observed magnitude in the dataset and includes two of the three strong shallow events identified in Section 3.

### GEOFON

Although GEOFON contains relatively few events overall, it includes one of the strongest and most hazardous earthquakes in the dataset.

This suggests that GEOFON is especially useful for monitoring significant seismic events rather than providing broad completeness.

### EMSC

EMSC contains many earthquakes overall, but most belong to the **Weak** and **Moderate** categories.

Strong earthquakes represent only a small proportion of this catalog.

### Side Dataset

The side dataset contains mostly moderate earthquakes and appears to have limited representation of strong events.

### Qualitative Comparison Table

| Source | Weak (< 4) | Moderate (4–6) | Strong (> 6) |
|--------|------------|----------------|--------------|
| EMSC | Excellent | Excellent | Limited |
| USGS | Limited | Excellent | Excellent |
| GEOFON | Very Limited | Moderate | Strong for major-event detection |
| Dataset | Limited | Moderate | Limited |

### Conclusion

The catalogs do not contribute equally across all magnitude ranges.

- **EMSC** is strongest for weak events
- **USGS** is strongest for moderate and strong events
- **GEOFON** is valuable for confirming major earthquakes

---

## 5. Scientific Interpretation of Recent Seismic Activity in Japan

### Magnitude Distribution

Most earthquakes fall within the **magnitude range of 3.0 to 5.0**, indicating that **low-to-moderate earthquakes dominate** recent seismic activity in the dataset.

Large earthquakes above **Magnitude 6** are relatively rare.

### Temporal Distribution

The scatter plot shows that earthquake magnitudes remain relatively stable over time.

No clear increasing or decreasing trend in earthquake magnitude is visible.

The apparent separation into two time clusters, around **2025** and **2026**, is more likely caused by differences in source datasets than by a genuine change in seismic behavior.

### Hourly Distribution

Earthquake frequency peaks around **11:00**.

However, earthquakes are driven by tectonic stress accumulation and release, not by daily human or environmental cycles.

Therefore, this hourly variation is most likely the result of **sampling variability** rather than a real physical pattern.

### Weekly Distribution

The dataset shows the highest number of earthquakes on **Wednesday**.

Scientifically, there is no established relationship between earthquake occurrence and weekdays.

This pattern should therefore be interpreted as **random variation in the sample**.

### Overall Scientific Conclusion

The analyzed dataset indicates that Japan experienced predominantly **low-to-moderate seismic activity** during the analyzed period.

Most earthquakes remained below **Magnitude 5**.

Only a few strong earthquakes exceeded **Magnitude 6**, and these were concentrated among **shallow events**, increasing their potential hazard near the Earth’s surface.

---

## 6. Recommendations for Combining Multiple Earthquake Catalogs

No individual earthquake catalog provides complete coverage of all seismic events.

Each source has distinct strengths and limitations. For this reason, combining multiple catalogs would significantly improve both **data completeness** and **data reliability**.

### Recommended Strategy

**Use EMSC for:**

- Detecting small earthquakes
- Improving completeness
- Increasing event density

**Use USGS for:**

- Moderate and large earthquakes
- Accurate magnitude estimation
- Global consistency

**Use GEOFON for:**

- Validation of significant earthquakes
- Cross-checking event parameters
- Improving confidence in major seismic events

### Data Integration Workflow

To maximize data quality, the following preprocessing steps are recommended:

1. Merge all catalogs.
2. Remove duplicate events using origin time, latitude, longitude, and magnitude.
3. Standardize datetime formats.
4. Normalize magnitude scales where necessary.
5. Validate major earthquakes across multiple catalogs.
6. Preserve unique small earthquakes detected only by EMSC.

### Conclusion

A merged catalog would provide a more complete and scientifically defensible representation of seismic activity than any single catalog alone.

---

## Final Conclusion

This comparative analysis demonstrates that each earthquake catalog captures different aspects of Japan’s seismic activity.

**EMSC** provides the most complete coverage of low-magnitude earthquakes and is therefore highly valuable for monitoring background seismicity.

**USGS** offers the most reliable coverage of moderate and strong earthquakes and includes the strongest events observed in this study.

**GEOFON** serves as an important complementary source for validating major seismic events.

The depth-based analysis further shows that the strongest earthquakes are predominantly **shallow**, making them the most hazardous due to their greater ability to produce strong surface shaking.

The database contains only **three records** that satisfy the official **Strong + shallow** hazard criteria. Two of these records almost certainly correspond to the same **M6.8, 10 km-deep earthquake near Uto/Kyushu**, independently reported by **GEOFON** and **USGS**. This confirms both the value of combining catalogs for cross-validation and the importance of duplicate-event detection during data integration.

Overall, integrating multiple earthquake catalogs provides a substantially more complete and scientifically reliable representation of seismic activity than relying on any single source. Such an approach reduces missing events, improves event validation, and strengthens both statistical and hazard-related analyses.
