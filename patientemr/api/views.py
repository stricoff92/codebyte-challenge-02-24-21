
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from api.lib.policy_data import (
    coalesce_strategies,
    api_wrapper as policy_data_api,
    sources as policy_data_sources
)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def policy_data(request):

    # Grab member_id from request query parameters
    member_id = request.query_params.get("member_id")
    if member_id is None:
        return Response({'error':'member_id is required'}, status.HTTP_400_BAD_REQUEST)
    try:
        member_id = int(member_id)
    except ValueError:
        return Response({'error':'invalid member_id'}, status.HTTP_400_BAD_REQUEST)

    # get coalesce strategy from request query parameters
    coalesce_strategy_name = request.query_params.get("coalesce_strategy")
    coalesce_strategy_name = coalesce_strategy_name or coalesce_strategies.DEFAULT_STRATEGY
    try:
        coalesce_strategy = coalesce_strategies.get_coalesce_stragety(
            coalesce_strategy_name)
    except coalesce_strategies.UnknownStrategyError:
        return Response(
            {'error':'unknown coalesce_strategy'}, status.HTTP_400_BAD_REQUEST)

    # check if we have this data cached
    if not request.query_params.get("bust_cache"):
        cached_response = policy_data_api.check_for_cached_response(
            member_id, coalesce_strategy_name)
        if cached_response is not None:
            return Response(cached_response, status.HTTP_200_OK)

    # fetch unmerged data from 3rd parties
    sources = [
        policy_data_sources.SourceAPI1(member_id),
        policy_data_sources.SourceAPI2(member_id),
        policy_data_sources.SourceAPI3(member_id),
    ]
    unmerged_policy_data = policy_data_api.fetch_data(sources)

    # merge data from 3rd parties
    coalesced_policy_data = coalesce_strategy(unmerged_policy_data)

    # cache coalesced data
    policy_data_api.set_cached_response(
        member_id, coalesce_strategy_name, coalesced_policy_data)


    return Response(coalesced_policy_data, status.HTTP_200_OK)
