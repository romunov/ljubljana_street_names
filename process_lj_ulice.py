from pathlib import Path
import pandas as pd

from plotnine import (
    ggplot,
    geom_jitter,
    aes,
    theme_bw,
    stat_summary_bin,
    ggsave,
)

pd.set_option("display.max_columns", 10)
pd.set_option("display.width", 200)

FIG_DIR = Path("figures")
FIG0 = FIG_DIR / "cesta_ulica_pot.pdf"

FIG_DIR.mkdir(exist_ok=True)

ucp = "ulica_cesta_pot"

xy = pd.read_csv("street_names.tsv", sep="\t", usecols=["ime", "leto", "obrazlozitev"])
# Cleanup
xy = xy[~xy.ime.isna()]
xy = xy[xy.leto > 1000]
xy[ucp] = "other"

xy.loc[xy.ime.str.contains("ulica"), ucp] = "ulica"
xy.loc[xy.ime.str.contains("cesta"), ucp] = "cesta"
xy.loc[xy.ime.str.contains("pot"), ucp] = "pot"

fig0 = (
    ggplot(xy, mapping=aes(x=ucp, y="leto"))
    + theme_bw()
    + geom_jitter(width=0.25, alpha=0.5)
    + stat_summary_bin(geom="pointrange", color="black", fill="red", size=1)
)

ggsave(fig0, filename=FIG0, width=4, height=10)
