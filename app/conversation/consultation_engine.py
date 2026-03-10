class ConsultationEngine:

    @staticmethod
    def generate_response(session, domain, signals, user_text):

        # conversation stage
        stage = session.consultation_stage or 1

        age = session.age
        dasha = signals.get("current_dasha")
        antardasha = signals.get("current_antardasha")
        driver = signals.get("primary_driver")

        # --------------------------
        # STAGE 1 → CHART INSIGHT
        # --------------------------
        if stage == 1:

            session.consultation_stage = 2

            return (
                f"Main Acharya Aryavrat bol raha hoon.\n\n"
                f"Aapki age abhi {age} saal hai aur yeh career build karne ka samay hota hai.\n\n"
                f"Is samay {driver} ka prabhav {domain} area ko activate kar raha hai.\n"
                f"Aapke chart mein {dasha} ki dasha aur {antardasha} ka antardasha chal raha hai.\n\n"
                f"Pehle mujhe yeh bataiye ki aapki current situation kya hai?"
            )

        # --------------------------
        # STAGE 2 → SITUATION
        # --------------------------
        elif stage == 2:

            session.consultation_stage = 3

            return (
                f"Agar aapne bataya ki '{user_text}', to is situation mein "
                f"{driver} ka influence practical decisions ko important banata hai.\n\n"
                f"Is stage par jaldbazi se bada decision lena theek nahi hota.\n\n"
                f"Aap chahein to main is situation ko strategy ke form mein samjha sakta hoon."
            )

        # --------------------------
        # STAGE 3 → STRATEGY
        # --------------------------
        elif stage == 3:

            session.consultation_stage = 4

            return (
                f"Strategy ke hisaab se aapko do cheezon par focus karna chahiye:\n\n"
                f"1) skill aur visibility increase karna\n"
                f"2) financial stability maintain karna\n\n"
                f"Agar aap chahein to main ise ek 30-day action plan mein tod sakta hoon."
            )

        # --------------------------
        # STAGE 4 → ACTION PLAN
        # --------------------------
        elif stage == 4:

            return (
                f"Agle 30 din ke liye simple action plan yeh ho sakta hai:\n\n"
                f"• week 1 → current position evaluate kariye\n"
                f"• week 2 → skills upgrade par focus kariye\n"
                f"• week 3 → networking aur opportunities explore kariye\n"
                f"• week 4 → decision clarity build kariye\n\n"
                f"Agar aap chahein to main bata sakta hoon ki "
                f"{dasha} period mein next opportunity kab strong ho sakti hai."
            )