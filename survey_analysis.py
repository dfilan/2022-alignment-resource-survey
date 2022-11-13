import csv
import functools
import math

import numpy as np

# Defining the fields we're working with
INVOLVEMENT_LEVELS = [
    "I have heard of AI alignment",
    "I am interested in AI alignment research",
    "I am trying to move into a technical AI alignment career",
    "I spend some of my time solving technical problems related to AI alignment",
    "I spend some of my time doing AI alignment field/community-building",
    "I spend some of my time facilitating technical AI alignment research in ways other than doing it directly",
    "I spend some of my time publicly communicating about AI alignment",
    "I am paid to work on technical AI alignment research",
    "I help run an organization with an AI alignment mission (e.g. CHAI, MIRI, Anthropic)",
]
RESOURCE_LIST = [
    "AGI Safety Fundamentals Course",
    "the AI Alignment Newsletter",
    "AXRP - the AI X-risk Research Podcast",
    "the ML Safety newsletter",
    "Human Compatible (book)",
    "The Alignment Problem (book)",
    "Rob Miles videos",
    "the Embedded Agency sequence on the Alignment Forum",
    "the Value Learning sequence on the Alignment Forum",
    "the Iterated Amplification sequence on the Alignment Forum",
    "the FLI podcast",
    "the 80,000 Hours podcast",
    "Life 3.0 (book)",
    "Superintelligence (book)",
    "AI Safety Camp",
    "AIRCS workshops",
    "the Machine Learning for Alignment Bootcamp",
    "the ARCHES agenda by Andrew Critch and David Krueger",
    "Unsolved Problems in ML Safety by Hendrycks et al",
    "Concrete Problems in AI Safety by Amodei et al",
    "Scalable agent alignment via reward modeling: a research direction by Leike et al (aka \"the recursive reward modelling agenda\")",
    "conversations with AI alignment researchers at conferences",
    "talks by AI alignment researchers",
    "the annual AI Alignment Literature Review and Charity Comparison",
]

# Processing the data into a manageable form

data = []
total_entries = 0
total_good_entries = 0
total_perfect_entries = 0

with open('ai-alignment-resource-survey.csv', newline='') as csvfile:
    my_reader = csv.DictReader(csvfile, delimiter=',')
    for i, row in enumerate(my_reader):
        total_entries += 1
        # only add to the data if they completed the survey
        if row['Time Finished (UTC)'] != '':
            total_good_entries += 1
            data_dict = {}
            involvement = row["How involved in AI alignment are you? Please select all that apply. (g4mdi50)"]
            for level in INVOLVEMENT_LEVELS:
                data_dict[level] = level in involvement
            years_interested = row['For how many years have you been interested in AI alignment research? Please enter an integer, rounded to the nearest year. (bu4zyb5)']
            years_interested = years_interested.split(' | ')[-1]
            data_dict['years_interested'] = float(years_interested) if years_interested != '' else 0
            years_paid = row['For how many years have you been paid to work on technical AI alignment research? Please enter an integer, rounded to the nearest year. (ub5lnfb)']
            years_paid = years_paid.split(' | ')[-1]
            data_dict['years_paid'] = float(years_paid) if years_paid != '' else 0
            resources = row['resources'][2:-2]
            resource_list = resources.split('\",\"')
            usefulness = row['Overall, how useful have you found {resource}? (okdtv5m)']
            usefulness_list = usefulness.split(' | ')
            recommend_new = row["How likely would you be to recommend {resource} as an AI alignment resource to a friend getting into AI alignment, who hadn\'t already read widely in the space? (xf22i7s)"]
            recommend_new_list = recommend_new.split(' | ')
            recommend_paid = row["How likely would you be to recommend {resource} as an AI alignment resource to a friend who is paid to do AI alignment research? (b51q4lo)"]
            recommend_paid_list = recommend_paid.split(' | ')
            # Check these lists are the same length so I can match them.
            # I messed up when creating the survey so if people pressed the
            # "back" button, their new response was appended to the same list,
            # rather than overwriting some variable thing.
            same_length = len(resource_list) == len(usefulness_list) and len(resource_list) == len(recommend_new_list) and len(resource_list) == len(recommend_paid_list)
            not_empty = len(resource_list) != 0
            filled_out = all([entry in RESOURCE_LIST for entry in resource_list])
            well_formatted = same_length and not_empty and filled_out
            if well_formatted:
                total_perfect_entries += 1
                data_dict['resource_ratings'] = {}
                for resource, use, rec_new, rec_paid in zip(resource_list,
                                                            usefulness_list,
                                                            recommend_new_list,
                                                            recommend_paid_list):
                    data_dict['resource_ratings'][resource] = {}
                    try:
                        data_dict['resource_ratings'][resource]['usefulness'] = int(use)
                    except ValueError:
                        pass
                    try:
                        data_dict['resource_ratings'][resource]['rec_new'] = int(rec_new)
                    except ValueError:
                        pass
                    try:
                        data_dict['resource_ratings'][resource]['rec_paid'] = int(rec_paid)
                    except ValueError:
                        pass
            data.append(data_dict)

# Now, for some fun data analysis

# I recommend commenting out everything you don't want to see / uncommenting stuff you do.
            
# print(data[1])
# print(f"{total_entries=}")
# print(f"{total_good_entries=}")
# print(f"{total_perfect_entries=}\n")


def num_with_this_true(involvement_level):
    return functools.reduce(lambda x, y: x + y[involvement_level], data, 0)

# for involvement_level in INVOLVEMENT_LEVELS:
#     num_that_involved = num_with_this_true(involvement_level)
#     print("Number that say", involvement_level, ":", num_that_involved)


def order_by_first_tup_element(my_dict):
    dict_list = list(my_dict.items())
    sorted_dict_list = sorted(dict_list, key=(lambda entry: entry[1][0]), reverse=True)
    return dict(sorted_dict_list)


def order_by_value(my_dict):
    dict_list = list(my_dict.items())
    sorted_dict_list = sorted(dict_list, key=(lambda entry: entry[1]), reverse=True)
    return dict(sorted_dict_list)


def get_total_tried(my_data):
    total_tried = {resource: 0 for resource in RESOURCE_LIST}
    for row in my_data:
        try:
            for resource in row["resource_ratings"]:
                total_tried[resource] += 1
        except KeyError:
            pass

    return order_by_value(total_tried)

# print("\nHow many people tried each resource:")
# print(get_total_tried(data))


def get_total_avg_usefulness(data_subset):
    usefulnesses = {resource: [] for resource in RESOURCE_LIST}
    for row in data_subset:
        try:
            for resource in row["resource_ratings"]:
                usefulnesses[resource].append(row["resource_ratings"][resource]["usefulness"])
        except KeyError:
            pass

    sems = {}
    for resource in RESOURCE_LIST:
        num_tried = len(usefulnesses[resource])
        if num_tried > 1:
            sems[resource] = np.std(usefulnesses[resource]) / math.sqrt(num_tried)
        
    average_usefulness = {}
    total_usefulness = {}
    for resource in RESOURCE_LIST:
        num_tried = len(usefulnesses[resource])
        if num_tried > 1:
            average_usefulness[resource] = (np.mean(usefulnesses[resource]), sems[resource])
            total_usefulness[resource] = (
                sum(usefulnesses[resource]), sems[resource] * num_tried
            )

    return (order_by_first_tup_element(total_usefulness),
            order_by_first_tup_element(average_usefulness))

# all_tot, all_avg = get_total_avg_usefulness(data)
# print("\nTotal usefulnesses of all resources:", all_tot)
# print("\nAverage usefulnesses of all resources:", all_avg)


def filtered_pop(my_data, involvement_level):
    return filter(lambda x: x[involvement_level], my_data)

def usefulness_in_filtered_pop(my_data, involvement_level):
    subset = filtered_pop(my_data, involvement_level)
    total, avg = get_total_avg_usefulness(subset)
    print("\nTotal usefulnesses among people who say", involvement_level)
    print(total)
    print("\nAverage usefulnesses among people who say", involvement_level)
    print(avg)

# usefulness_in_filtered_pop(data, "I am trying to move into a technical AI alignment career")

# usefulness_in_filtered_pop(data, "I spend some of my time solving technical problems related to AI alignment")

# usefulness_in_filtered_pop(data, "I spend some of my time facilitating technical AI alignment research in ways other than doing it directly")

# usefulness_in_filtered_pop(data, "I am paid to work on technical AI alignment research")

# usefulness_in_filtered_pop(data, "I help run an organization with an AI alignment mission (e.g. CHAI, MIRI, Anthropic)")

def recommend_to(data_subset):
    recs_new = {resource: [] for resource in RESOURCE_LIST}
    recs_paid = {resource: [] for resource in RESOURCE_LIST}
    for row in data_subset:
        try:
            for resource in row["resource_ratings"]:
                recs_new[resource].append(row["resource_ratings"][resource]["rec_new"])
                recs_paid[resource].append(row["resource_ratings"][resource]["rec_paid"])
        except KeyError:
            pass

    rec_new_stats = {}
    rec_paid_stats = {}
    for resource in RESOURCE_LIST:
        num_tried_new = len(recs_new[resource])
        num_tried_paid = len(recs_paid[resource])
        if num_tried_new > 1:
            rec_new_stats[resource] = (np.mean(recs_new[resource]),
                                       np.std(recs_new[resource]) / math.sqrt(num_tried_new))
        if num_tried_paid > 1:
            rec_paid_stats[resource] = (np.mean(recs_paid[resource]),
                                        np.std(recs_paid[resource]) / math.sqrt(num_tried_paid))

    return order_by_first_tup_element(rec_new_stats), order_by_first_tup_element(rec_paid_stats)

# total_rec_new, total_rec_paid = recommend_to(data)
# print("\nHow much everyone would recommend stuff to people getting into alignment:")
# print(total_rec_new)

# print("\nHow much everyone would recommend stuff to people paid to do alignment research:")
# print(total_rec_paid)

# old_rec_new, old_rec_old = recommend_to(filtered_pop(data, "I am paid to work on technical AI alignment research"))

# print("\nHow much AI alignment professionals recommend things to people getting into alignment:")
# print(old_rec_new)

# print("\nHow much AI alignment professionals recommend things to their peers:")
# print(old_rec_old)

# new_rec_new, _ = recommend_to(filtered_pop(data, "I am trying to move into a technical AI alignment career"))

# print("\nHow much people trying to move into AI alignment recommend things to their peers:")
# print(new_rec_new)

# fac_rec_new, fac_rec_paid = recommend_to(filtered_pop(data, "I spend some of my time facilitating technical AI alignment research in ways other than doing it directly"))

# print("\nfac_rec_new:", fac_rec_new)

# print("\nfac_rec_paid:", fac_rec_paid)

# run_rec_new, run_rec_paid = recommend_to(filtered_pop(data, "I help run an organization with an AI alignment mission (e.g. CHAI, MIRI, Anthropic)"))

# print("\nrun_rec_new:", run_rec_new)

# print("\nrun_rec_paid:", run_rec_paid)
