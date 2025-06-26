import time
import json
import requests
from typing import Mapping
from werkzeug import Request, Response
from dify_plugin import Endpoint


class DifyWpRagEndpoint(Endpoint):
    def _invoke(self, r: Request, values: Mapping, settings: Mapping) -> Response:
        """
        Invokes the endpoint with the given request.
        """
        # Parse JSON from the incoming request
        body = r.json

        pipeline_id = body.get("knowledge_id")
        query = body.get("query")

        # Extract retrieval settings with sensible defaults
        retrieval_settings = body.get("retrieval_setting")
        top_k = retrieval_settings.get("top_k")
        score_threshold = retrieval_settings.get("score_threshold")

        site_id = settings.get("wp_rag_site_id")
        api_key = settings.get("wp_rag_api_key")

        base_url = 'https://wp-rag.mobalab.net'
        url = base_url + '/api/sites/' + site_id + '/posts/search'
        params = {'q': query, 'limit': top_k, 'score_threshold': score_threshold}
        headers = {'Content-Type': 'application/json', 'X-Api-Key': api_key}

        response = requests.get(url, params, headers=headers)
        results = []
        for record in response.json()['search_results']:
            result = {
                "metadata": {
                    "path": record['post']['url'],
                    "description": ''
                },
                "score": record['score'],
                "title": record['post']['title'],
                "content": record['post']['content']
            }
            results.append(result)

        return Response(json.dumps({"records": results}), status=200, content_type="application/json")
