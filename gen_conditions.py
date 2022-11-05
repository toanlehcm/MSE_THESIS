import constants


def condition_common(evidences, matched_labels, returned_labels, conditions):
    ##
    # Condition common: real estate, position, direction, floor....
    #
    # Return:
    #       returned_labels.
    #       conditions.
    # #

    attrs = [constants.LABEL_REAL_ESTATE_TYPE, constants.LABEL_REAL_ESTATE_SUB_TYPE, \
              constants.LABEL_POSITION, constants.LABEL_DIRECTION, \
              constants.LABEL_FRONT_LENGTH, constants.LABEL_ROAD_WIDTH, \
              constants.LABEL_FLOOR, constants.LABEL_BED_ROOM, constants.LABEL_LIVING_ROOM, constants.LABEL_BATH_ROOM, \
              constants.LABEL_SURROUNDING, constants.LABEL_PROJECT_NAME, \
              constants.LABEL_LEGAL, constants.LABEL_TRANSACTION]

    key2dbcol = {
        'tang': constants.LABEL_FLOOR,
        'ban cong': constants.LABEL_FLOOR_BAN_CONG,
        'gac': constants.LABEL_FLOOR_GAC,
        'ham': constants.LABEL_FLOOR_HAM,
        'lung': constants.LABEL_FLOOR_LUNG,
        'san thuong': constants.LABEL_FLOOR_SAN_THUONG,
        'tret': constants.LABEL_FLOOR_TRET
    }

    for attr in attrs:
        if attr in evidences:
            if attr == constants.LABEL_FLOOR:
                for val in evidences[attr]:
                    target_k = key2dbcol[val['type']]
                    target_v = val['value']

                    returned_labels = recheck_returned_labels(
                        matched_labels, returned_labels, target_k)

                    conditions.append(f"{target_k}.individual = '{target_v}'")
            else:
                returned_labels = recheck_returned_labels(
                    matched_labels, returned_labels, attr)

                if attr == constants.LABEL_REAL_ESTATE_TYPE or attr == constants.LABEL_REAL_ESTATE_SUB_TYPE:
                    conditions.append(
                        f"{attr}.individual IN {evidences[attr]}")
                else:
                    conditions.append(
                        f"{attr}.individual = '{evidences[attr][0]}'")

    return [returned_labels, conditions]


def condition_location(evidences, matched_labels, returned_labels, conditions):
    ##
    # Condition for city, district, ward, street.
    #
    # Return:
    #       returned_labels.
    #       conditions.
    # #

    loc_attrs = [
        constants.LABEL_DISTRICT, constants.LABEL_CITY, constants.LABEL_WARD,
        constants.LABEL_STREET
    ]

    for attr in loc_attrs:
        if attr in evidences:
            returned_labels = recheck_returned_labels(matched_labels,
                                                      returned_labels, attr)

            conditions.append(f"{attr}.individual = '{evidences[attr][0]}'")

    return [returned_labels, conditions]


def condition_price_n_area(is_price, evidences, matched_labels,
                           returned_labels, conditions):
    ##
    # Condition for price and area.
    #
    # Return:
    #       returned_labels.
    #       conditions.
    # #

    OFFSET_CONST = 0.1

    condition_item = is_price and constants.LABEL_PRICE or constants.LABEL_AREA

    if condition_item in evidences:
        for ele in evidences[condition_item][:1]:
            low, high = ele

            if high is None:
                high = low + low * OFFSET_CONST
                low = low - low * OFFSET_CONST

            returned_labels = recheck_returned_labels(matched_labels,
                                                      returned_labels,
                                                      condition_item)

            conditions.append(
                f"'{low}' <= {condition_item}.individual <= '{high}'")

    return [returned_labels, conditions]


def condition_usage(evidences, matched_labels, returned_labels, conditions):
    ##
    # Condition for usage.
    #
    # Return:
    #       returned_labels.
    #       conditions.
    # #

    if constants.LABEL_USAGE in evidences:
        returned_labels = recheck_returned_labels(matched_labels,
                                                  returned_labels,
                                                  constants.LABEL_USAGE)

        conditions.append("({})".format(" OR ".join([
            f"{constants.LABEL_USAGE}.individual LIKE '%, {x},%' + 'OR {constants.LABEL_USAGE}.individual LIKE '{x}, %' OR {constants.LABEL_USAGE}.individual LIKE '%, {x}'"
            for x in evidences[constants.LABEL_USAGE]
        ])))

    return [returned_labels, conditions]


def recheck_returned_labels(matched_labels, returned_labels, attr):
    ##
    # Remove the label which has a condition from returned_label.
    #
    # Argument:
    #     matched_labels: The labels which were matched.
    #     returned_labels: The labels which were returned.
    #     attr: The attribute that you want to check for.
    # Return:
    #     returned_labels.
    # #

    for match_label in matched_labels:
        if attr in match_label:
            returned_labels.remove(match_label)

    return returned_labels
