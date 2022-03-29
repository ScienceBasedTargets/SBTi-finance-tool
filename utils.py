import pandas as pd
import numpy as np
import copy as copy
import random


def print_aggregations(aggregations):
    aggregations = aggregations.dict()
    print("{:<10s} {:<10s} {}".format('Timeframe', 'Scope', 'Temp score'))
    for time_frame, time_frame_values in aggregations.items():
        if time_frame_values:
            for scope, scope_values in time_frame_values.items():
                if scope_values:
                    print("{:<10s} {:<10s} {:.2f}".format(time_frame, scope, scope_values["all"]["score"]))


def print_percentage_default_scores(aggregations):
    aggregations = aggregations.dict()
    print("{:<10s} {:<10s} {}".format('Timeframe', 'Scope', '% Default score'))
    for time_frame, time_frame_values in aggregations.items():
        if time_frame_values:
            for scope, scope_values in time_frame_values.items():
                if scope_values:
                    print("{:<10s} {:<10s} {:.2f}".format(time_frame, scope, scope_values['influence_percentage']))


def print_scenario_gain(actual_aggregations, scenario_aggregations):
    print("Actual portfolio temperature score")
    print_aggregations(actual_aggregations)
    print()
    print("Scenario portfolio temperature score")
    print_aggregations(scenario_aggregations)


def print_grouped_scores(aggregations):
    aggregations = aggregations.dict()
    for time_frame, time_frame_values in aggregations.items():
        if time_frame_values:
            for scope, scope_values in time_frame_values.items():
                if scope_values:
                    print()
                    print("{:<25s}{}".format('', 'Temp score'))
                    print("{} - {}".format(time_frame, scope))
                    for group, aggregation in scope_values["grouped"].items():
                        print("{:<25s}{t:.2f}".format(group, t=aggregation["score"]))


def collect_company_contributions(aggregated_portfolio, amended_portfolio, analysis_parameters):
    timeframe, scope, grouping = analysis_parameters
    scope = str(scope[0])
    timeframe = str(timeframe[0]).lower()
    company_names = []
    relative_contributions = []
    temperature_scores = []
    for contribution in aggregated_portfolio[timeframe][scope]['all']['contributions']:
        company_names.append(contribution.company_name)
        relative_contributions.append(contribution.contribution_relative)
        temperature_scores.append(contribution.temperature_score)
    company_contributions = pd.DataFrame(data={'company_name': company_names, 'contribution': relative_contributions, 'temperature_score': temperature_scores})
    additional_columns = ['company_name', 'company_id', 'company_market_cap', 'investment_value'] + grouping
    company_contributions = company_contributions.merge(right=amended_portfolio[additional_columns], how='left', on='company_name')
    company_contributions['portfolio_percentage'] = 100 * company_contributions['investment_value'] / company_contributions['investment_value'].sum()
    company_contributions['ownership_percentage'] = 100 * company_contributions['investment_value'] / company_contributions['company_market_cap']
    company_contributions = company_contributions.sort_values(by='contribution', ascending=False)
    return company_contributions


def plot_grouped_statistics(aggregated_portfolio, company_contributions, analysis_parameters):
    import matplotlib.pyplot as plt

    timeframe, scope, grouping = analysis_parameters
    scope = str(scope[0])
    timeframe = str(timeframe[0]).lower()

    sector_investments = company_contributions.groupby(grouping).investment_value.sum().values
    sector_contributions = company_contributions.groupby(grouping).contribution.sum().values
    sector_names = company_contributions.groupby(grouping).contribution.sum().keys()
    sector_temp_scores = [aggregation.score for aggregation in aggregated_portfolio[timeframe][scope]['grouped'].values()]

    sector_temp_scores, sector_names, sector_contributions, sector_investments = \
        zip(*sorted(zip(sector_temp_scores, sector_names, sector_contributions, sector_investments), reverse=True))

    fig = plt.figure(figsize=[10, 7.5])
    ax1 = fig.add_subplot(231)
    ax1.set_prop_cycle(plt.cycler("color", plt.cm.tab20.colors))
    ax1.pie(sector_investments, autopct='%1.0f%%', pctdistance=1.25, labeldistance=2)
    ax1.set_title("Investments", pad=15)


    ax2 = fig.add_subplot(232)
    ax2.set_prop_cycle(plt.cycler("color", plt.cm.tab20.colors))
    ax2.pie(sector_contributions, autopct='%1.0f%%', pctdistance=1.25, labeldistance=2)
    ax2.legend(labels=sector_names, bbox_to_anchor=(1.2, 1), loc='upper left')
    ax2.set_title("Contributions", pad=15)

    ax3 = fig.add_subplot(212)
    ax3.bar(sector_names, sector_temp_scores)
    ax3.set_title("Temperature scores per " + grouping[0])
    ax3.set_ylabel("Temperature score")
    for label in ax3.get_xticklabels():
        label.set_rotation(45)
        label.set_ha('right')
    ax3.axhline(y=1.5, linestyle='--', color='k')


def anonymize(portfolio, provider):
    portfolio_companies = portfolio['company_name'].unique()
    for index, company_name in enumerate(portfolio_companies):
        portfolio.loc[portfolio['company_name'] == company_name, 'company_id'] = 'C' + str(index + 1)
        portfolio.loc[portfolio['company_name'] == company_name, 'company_isin'] = 'C' + str(index + 1)
        provider.data['fundamental_data'].loc[provider.data['fundamental_data']['company_name'] == company_name, 'company_id'] = 'C' + str(index + 1)
        provider.data['fundamental_data'].loc[provider.data['fundamental_data']['company_name'] == company_name, 'company_isic'] = 'C' + str(index + 1)
        provider.data['target_data'].loc[provider.data['target_data']['company_name'] == company_name, 'company_id'] = 'C' + str(index + 1)
        portfolio.loc[portfolio['company_name'] == company_name, 'company_name'] = 'Company' + str(
            index + 1)
        provider.data['fundamental_data'].loc[provider.data['fundamental_data']['company_name'] == company_name, 'company_name'] = 'Company' + str(
            index + 1)
        provider.data['target_data'].loc[provider.data['target_data']['company_name'] == company_name, 'company_name'] = 'Company' + str(
            index + 1)
    for index, company_name in enumerate(provider.data['fundamental_data']['company_name'].unique()):
        if company_name not in portfolio['company_name'].unique():
            provider.data['fundamental_data'].loc[provider.data['fundamental_data']['company_name'] == company_name, 'company_id'] = '_' + str(index + 1)
            provider.data['fundamental_data'].loc[provider.data['fundamental_data']['company_name'] == company_name, 'company_name'] = 'Company_' + str(
                index + 1)
    return portfolio, provider


def plot_grouped_heatmap(grouped_aggregations, analysis_parameters):
    import matplotlib.pyplot as plt
    import matplotlib

    timeframe, scope, grouping = analysis_parameters
    scope = str(scope[0])
    timeframe = str(timeframe[0]).lower()
    group_1, group_2 = grouping

    aggregations = grouped_aggregations[timeframe][scope].grouped
    combinations = list(aggregations.keys())

    groups = {group_1: [], group_2: []}
    for combination in combinations:
        item_group_1, item_group_2 = combination.split('-')
        if item_group_1 not in groups[group_1]:
            groups[group_1].append(item_group_1)
        if item_group_2 not in groups[group_2]:
            groups[group_2].append(item_group_2)
    groups[group_1] = sorted(groups[group_1])
    groups[group_2] = sorted(groups[group_2])

    grid = np.zeros((len(groups[group_2]), len(groups[group_1])))
    for i, item_group_2 in enumerate(groups[group_2]):
        for j, item_group_1 in enumerate(groups[group_1]):
            key = item_group_1+'-'+item_group_2
            if key in combinations:
                grid[i, j] = aggregations[item_group_1+'-'+item_group_2].score
            else:
                grid[i, j] = np.nan

    current_cmap = copy.copy(matplotlib.cm.get_cmap('OrRd'))
    current_cmap.set_bad(color='grey', alpha=0.4)

    fig = plt.figure(figsize=[0.9*len(groups[group_1]), 0.8*len(groups[group_2])])
    ax = fig.add_subplot(111)
    im = ax.pcolormesh(grid, cmap=current_cmap)
    ax.set_xticks(0.5 + np.arange(0, len(groups[group_1])))
    ax.set_yticks(0.5 + np.arange(0, len(groups[group_2])))
    ax.set_yticklabels(groups[group_2])
    ax.set_xticklabels(groups[group_1])
    for label in ax.get_xticklabels():
        label.set_rotation(45)
        label.set_ha('right')
    fig.colorbar(im, ax=ax)
    ax.set_title("Temperature score per " + group_2 + " per " + group_1)


def get_contributions_per_group(aggregations, analysis_parameters, group):
    timeframe, scope, grouping = analysis_parameters
    scope = str(scope[0])
    timeframe = str(timeframe[0]).lower()
    aggregations = aggregations.dict()

    contributions = aggregations[timeframe][scope]['grouped'][group]['contributions']
    contributions = pd.DataFrame(contributions)
    columns = ['group'] + contributions.columns.tolist()
    contributions['group'] = group
    contributions = contributions[columns]
    contributions.drop(columns=['contribution'], inplace=True)
    return contributions