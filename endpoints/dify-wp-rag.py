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
        # Note that top_k and score_threshold are ignored at this moment.
        params = {'q': query, 'top_k': top_k, 'score_threshold': score_threshold}
        headers = {'Content-Type': 'application/json', 'X-Api-Key': api_key}

        response = requests.get(url, params, headers=headers)
        results = []
        for record in response.json()['search_results']:
            result = {
                "metadata": {
                    "path": record['url'],
                    "description": ''
                },
                "score": 0.8, #TODO Not implemented on the API side
                "title": record['title'],
                "content": record['body']
            }
            results.append(result)

        return Response(json.dumps({"records": results}), status=200, content_type="application/json")
