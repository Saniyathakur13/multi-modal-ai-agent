def validate_medical_data(data):

    abnormalities = []

    # -------------------------
    # HEMOGLOBIN
    # -------------------------
    hemoglobin = data.get("hemoglobin")

    try:

        if hemoglobin is not None:

            hemoglobin = float(hemoglobin)

            # OCR correction
            if hemoglobin > 50:
                hemoglobin = hemoglobin / 10

            data["hemoglobin"] = hemoglobin

            if hemoglobin < 13:
                abnormalities.append(
                    f"Low hemoglobin detected: {hemoglobin} g/dL"
                )

    except:
        data["hemoglobin"] = None

    # -------------------------
    # WBC
    # -------------------------
    wbc = data.get("wbc")

    try:

        if wbc is not None:

            wbc = float(wbc)

            data["wbc"] = wbc

            if wbc < 4000:
                abnormalities.append(
                    f"Low WBC count detected: {wbc}"
                )

    except:
        data["wbc"] = None

    # -------------------------
    # RBC
    # -------------------------
    rbc = data.get("rbc")

    try:

        if rbc is not None:

            rbc = float(rbc)

            # OCR decimal correction
            if rbc > 20:
                rbc = rbc / 10

            data["rbc"] = rbc

            if rbc < 4:
                abnormalities.append(
                    f"Low RBC count detected: {rbc}"
                )

    except:
        data["rbc"] = None

    # -------------------------
    # PLATELETS
    # -------------------------
    platelets = data.get("platelets")

    try:

        if platelets is not None:

            if isinstance(platelets, str):

                if "-" in platelets:
                    platelets = platelets.split("-")[0]

                platelets = platelets.replace(",", "").strip()

            platelets = float(platelets)

            data["platelets"] = platelets

            if platelets < 150000:
                abnormalities.append(
                    f"Low platelet count detected: {platelets}"
                )

    except:
        data["platelets"] = None

    # -------------------------
    # VALIDATION FINDINGS
    # -------------------------
    data["validation_findings"] = abnormalities

    return data