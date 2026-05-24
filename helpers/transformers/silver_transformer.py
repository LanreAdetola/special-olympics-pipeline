"""Silver transformer.
Cleans and standardises raw DataFrames.
"""

import re
import pandas as pd


class SilverTransformer:
    def transform(self, raw: dict) -> dict:
        print("\n--- Silver: Cleaning and standardising ---")
        return {
            "results": self._clean_results(raw["results"]),
            "clubs": self._clean_clubs(raw["clubs"]),
            "certifications": self._clean_certifications(raw["certifications"]),
        }

    def _clean_results(self, df: pd.DataFrame) -> pd.DataFrame:
        print("  [SILVER] Cleaning results...")
        df = df.copy()

        df.columns = [c.strip().lower().replace(" ", "_").replace("(", "").replace(")", "") for c in df.columns]

        if "summary_all" not in df.columns:
            df["summary_all"] = None

        gender_map = {"Male": "M", "Female": "F", "Unknown": "U"}
        df["gender"] = df["gender"].map(gender_map).fillna("U")

        df["score_numeric"] = df["score"].apply(self._parse_score)

        place_map = {
            "1st": 1,
            "2nd": 2,
            "3rd": 3,
            "4th": 4,
            "5th": 5,
            "6th": 6,
            "7th": 7,
            "8th": 8,
        }
        df["place_numeric"] = df["place"].map(place_map)

        disqualified = {"DQ", "DNC", "DNT"}
        did_not_start = {"DNS", "DNF"}
        df["is_dq"] = df["place"].isin(disqualified)
        df["is_dns"] = df["place"].isin(did_not_start)

        df["age_group"] = df["summary_all"].apply(self._extract_age_group)
        df["event_code"] = df["event"].apply(self._extract_event_code)
        df["sport_code"] = df["event_code"].apply(self._extract_sport_code)

        sport_normalise = {
            "Swimming": "Aquatics/Swimming",
            "Aquatics": "Aquatics/Swimming",
            "Gymnastic (Artistic)": "Gymnastics (Artistic)",
            "Gymnastic (Rhythmic)": "Gymnastics (Rhythmic)",
            "Football": "Football/Soccer",
            "Soccer": "Football/Soccer",
        }
        df["sport"] = df["sport"].replace(sport_normalise)

        df["club"] = df["club"].str.strip().str.upper()

        before = len(df)
        df = df[df["code"].notna() & (df["code"].str.strip() != "")]
        print(f"    Dropped {before - len(df)} rows with missing athlete code")

        print(f"    Results silver: {len(df):,} rows")
        return df

    def _clean_clubs(self, df: pd.DataFrame) -> pd.DataFrame:
        print("  [SILVER] Cleaning clubs...")
        df = df.copy()
        df.columns = [c.strip() for c in df.columns]

        df["Name"] = df["Name"].str.strip().str.upper()

        flag_cols = [c for c in df.columns if c.startswith("Participation")]
        for col in flag_cols:
            df[col] = df[col].fillna(False).astype(bool)

        print(f"    Clubs silver: {len(df):,} rows")
        return df

    def _clean_certifications(self, df: pd.DataFrame) -> pd.DataFrame:
        print("  [SILVER] Cleaning certifications...")
        df = df.copy()

        df["Gender"] = df["Gender"].fillna("U").replace({"U": "U", "M": "M", "F": "F"})
        df["Club"] = df["Club"].str.strip().str.upper()

        cert_cols = [c for c in df.columns if "SOB has this certificate" in c]
        for col in cert_cols:
            df[col] = df[col].fillna(0).astype(bool)

        print(f"    Certifications silver: {len(df):,} rows")
        return df

    @staticmethod
    def _parse_score(score) -> float:
        if pd.isna(score):
            return None
        s = str(score).strip()

        time_match = re.match(r"(\d+)\s*min,\s*([\d.]+)\s*sec", s)
        if time_match:
            minutes = float(time_match.group(1))
            seconds = float(time_match.group(2))
            return round(minutes * 60 + seconds, 3)

        points_match = re.match(r"([\d.]+)\s*points?", s)
        if points_match:
            return float(points_match.group(1))

        try:
            return float(s)
        except ValueError:
            return None

    @staticmethod
    def _extract_age_group(summary) -> str:
        if pd.isna(summary):
            return None
        match = re.search(r"(\d{1,2}[-–]\s*\d{1,2}|\d{2}\+)", str(summary))
        return match.group(0).replace(" ", "") if match else None

    @staticmethod
    def _extract_event_code(event) -> str:
        if pd.isna(event):
            return None
        match = re.match(r"^([A-Z]{1,4}\d{1,3}[A-Z]?)", str(event).strip())
        return match.group(1) if match else str(event).strip().split(" ")[0]

    @staticmethod
    def _extract_sport_code(event_code) -> str:
        if pd.isna(event_code):
            return None
        match = re.match(r"^([A-Z]+)", str(event_code))
        return match.group(1) if match else None
