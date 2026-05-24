"""gold transformer.
aggregates and standardises silver dataFrames.
"""

import pandas as pd


class GoldTransformer:
    def transform(self, silver: dict) -> dict:
        print("\n--- Gold: Building star schema tables ---")
        results = silver["results"]
        clubs = silver["clubs"]
        certs = silver["certifications"]

        dim_sport = self._build_dim_sport(results)
        dim_event = self._build_dim_event(results, dim_sport)
        dim_club = self._build_dim_club(clubs)
        dim_club = self._add_missing_clubs(dim_club, results)
        dim_athlete = self._build_dim_athlete(certs, results)
        dim_date = self._build_dim_date(results)
        fact = self._build_fact_results(results, dim_athlete, dim_club, dim_sport, dim_event, dim_date)

        return {
            "dim_sport": dim_sport,
            "dim_event": dim_event,
            "dim_club": dim_club,
            "dim_athlete": dim_athlete,
            "dim_date": dim_date,
            "fact_results": fact,
        }

    def _build_dim_sport(self, results: pd.DataFrame) -> pd.DataFrame:
        print("  [GOLD] Building dim_sport...")
        df = results[["sport"]].drop_duplicates().dropna(subset=["sport"])
        df = df.rename(columns={"sport": "sport_name"})

        code_df = (
            results[["sport", "sport_code"]]
            .dropna()
            .groupby("sport")["sport_code"]
            .agg(lambda x: x.mode().iloc[0] if len(x) > 0 else None)
            .reset_index()
            .rename(columns={"sport": "sport_name", "sport_code": "sport_code"})
        )

        df = df.merge(code_df, on="sport_name", how="left")
        df = df.sort_values("sport_name").reset_index(drop=True)
        df.insert(0, "sport_key", range(1, len(df) + 1))
        print(f"    {len(df)} sports")
        return df

    def _build_dim_event(self, results: pd.DataFrame, dim_sport: pd.DataFrame) -> pd.DataFrame:
        print("  [GOLD] Building dim_event...")
        df = results[["event", "event_code", "sport"]].drop_duplicates(subset=["event"])
        df = df.dropna(subset=["event"])
        df = df.rename(columns={"event": "event_raw"})
        df["event_name"] = df["event_raw"].apply(self._extract_event_name)

        df = df.merge(dim_sport[["sport_key", "sport_name"]], left_on="sport", right_on="sport_name", how="left")
        df = df.sort_values("event_raw").reset_index(drop=True)
        df.insert(0, "event_key", range(1, len(df) + 1))
        df = df[["event_key", "sport_key", "event_raw", "event_code", "event_name"]]
        print(f"    {len(df)} events")
        return df

    def _build_dim_club(self, clubs: pd.DataFrame) -> pd.DataFrame:
        print("  [GOLD] Building dim_club...")
        df = clubs.copy()
        df = df.rename(
            columns={
                "Group number": "group_number",
                "Name": "club_name",
                "Primary language": "primary_language",
                "Province": "province",
                "City": "city",
                "Country": "country",
            }
        )

        flag_cols = [c for c in clubs.columns if c.startswith("Participation")]
        flag_rename = {c: c.lower().replace(" ", "_") for c in flag_cols}
        df = df.rename(columns=flag_rename)

        keep = ["club_name", "group_number", "province", "city", "country", "primary_language"] + list(flag_rename.values())
        df = df[[c for c in keep if c in df.columns]]

        df = df.sort_values("club_name").reset_index(drop=True)
        df.insert(0, "club_key", range(1, len(df) + 1))
        print(f"    {len(df)} clubs")
        return df

    def _add_missing_clubs(self, dim_club: pd.DataFrame, results: pd.DataFrame) -> pd.DataFrame:
        known = set(dim_club["club_name"].str.upper())
        result_clubs = set(results["club"].dropna().str.upper().unique())
        missing = result_clubs - known

        if missing:
            extras = pd.DataFrame({"club_name": sorted(missing)})
            extras["group_number"] = None
            extras["province"] = "Unknown"
            extras["city"] = None
            extras["country"] = None
            extras["primary_language"] = None
            dim_club = pd.concat([dim_club, extras], ignore_index=True)
            dim_club = dim_club.sort_values("club_name").reset_index(drop=True)
            dim_club["club_key"] = range(1, len(dim_club) + 1)
            print(f"    Added {len(missing)} historical clubs not in master file")

        return dim_club

    def _build_dim_athlete(self, certs: pd.DataFrame, results: pd.DataFrame) -> pd.DataFrame:
        print("  [GOLD] Building dim_athlete...")
        athletes = certs[certs["Person type"] == "Athlete"].copy()
        athletes = athletes.rename(columns={"Code": "code", "Gender": "gender", "DOB": "dob"})

        cert_col_map = {
            "Mental Handicap (SOB has this certificate)": "has_mental_handicap_cert",
            "Parents Consent (SOB has this certificate)": "has_parents_consent",
            "HAP (SOB has this certificate)": "has_hap_cert",
            "Unified Partner (SOB has this certificate)": "is_unified_partner",
        }
        athletes = athletes.rename(columns=cert_col_map)
        athletes = athletes.drop_duplicates(subset=["code"])

        result_codes = set(results["code"].dropna().unique())
        cert_codes = set(athletes["code"].dropna().unique())
        missing = result_codes - cert_codes
        if missing:
            extra = pd.DataFrame({"code": list(missing)})
            athletes = pd.concat([athletes, extra], ignore_index=True)
            print(f"    Added {len(missing)} athletes found in results but not certifications")

        keep = [
            "code",
            "gender",
            "dob",
            "has_mental_handicap_cert",
            "has_parents_consent",
            "has_hap_cert",
            "is_unified_partner",
        ]
        athletes = athletes[[c for c in keep if c in athletes.columns]]
        athletes = athletes.sort_values("code").reset_index(drop=True)
        athletes.insert(0, "athlete_key", range(1, len(athletes) + 1))
        print(f"    {len(athletes)} athletes")
        return athletes

    def _build_dim_date(self, results: pd.DataFrame) -> pd.DataFrame:
        print("  [GOLD] Building dim_date...")
        years = sorted(results["edition_year"].dropna().unique())
        df = pd.DataFrame({"year": years})
        df["edition_year"] = df["year"]

        year_to_edition = {y: i + 1 for i, y in enumerate(years)}
        df["edition_number"] = df["year"].map(year_to_edition)
        df["is_post_covid"] = df["year"] >= 2022

        df.insert(0, "date_key", range(1, len(df) + 1))
        print(f"    {len(df)} editions")
        return df

    def _build_fact_results(
        self,
        results: pd.DataFrame,
        dim_athlete: pd.DataFrame,
        dim_club: pd.DataFrame,
        dim_sport: pd.DataFrame,
        dim_event: pd.DataFrame,
        dim_date: pd.DataFrame,
    ) -> pd.DataFrame:
        print("  [GOLD] Building fact_results...")
        df = results.copy()

        athlete_map = dim_athlete.set_index("code")["athlete_key"]
        club_map = dim_club.set_index("club_name")["club_key"]
        sport_map = dim_sport.set_index("sport_name")["sport_key"]
        event_map = dim_event.set_index("event_raw")["event_key"]
        date_map = dim_date.set_index("year")["date_key"]

        df["athlete_key"] = df["code"].map(athlete_map)
        df["club_key"] = df["club"].map(club_map)
        df["sport_key"] = df["sport"].map(sport_map)
        df["event_key"] = df["event"].map(event_map)
        df["date_key"] = df["edition_year"].map(date_map)

        fact = df[
            [
                "athlete_key",
                "club_key",
                "sport_key",
                "event_key",
                "date_key",
                "place",
                "place_numeric",
                "score",
                "score_numeric",
                "is_dq",
                "is_dns",
                "age",
                "role",
                "edition_year",
            ]
        ].copy()

        fact = fact.rename(columns={"place": "place_raw", "score": "score_raw", "age": "age_at_competition"})
        fact.insert(0, "result_id", range(1, len(fact) + 1))

        unmatched_athletes = fact["athlete_key"].isna().sum()
        unmatched_clubs = fact["club_key"].isna().sum()
        print(f"    Unmatched athletes: {unmatched_athletes:,}")
        print(f"    Unmatched clubs:    {unmatched_clubs:,}")
        print(f"    fact_results: {len(fact):,} rows")
        return fact

    @staticmethod
    def _extract_event_name(event_raw) -> str:
        if pd.isna(event_raw):
            return None
        parts = str(event_raw).split(" - ", 1)
        return parts[1].strip() if len(parts) > 1 else str(event_raw).strip()
