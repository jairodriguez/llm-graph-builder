# --- Environment setup ---
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())  # Load your .env automatically

from fastapi import FastAPI
import os

# Temporary debug endpoint to verify env loading
app = FastAPI()

@app.get("/__env_debug")
def env_debug():
    keys = [
        "LLM_MODEL_CONFIG_ollama_llama2",
        "DEFAULT_DIFFBOT_CHAT_MODEL",
        "GRAPH_CLEANUP_MODEL",
        "OPENAI_API_KEY"
    ]
    return {k: os.getenv(k) for k in keys}

# --- Existing imports below ---
from fastapi import File, UploadFile, Form, Request, HTTPException
from fastapi_health import health
from fastapi.middleware.cors import CORSMiddleware
from src.main import *
from src.QA_integration import *
from src.shared.common_fn import *
from src.shared.llm_graph_builder_exception import LLMGraphBuilderException
import uvicorn
import asyncio
import base64
from langserve import add_routes
from langchain_google_vertexai import ChatVertexAI
from src.api_response import create_api_response
from src.graphDB_dataAccess import graphDBdataAccess
from src.graph_query import get_graph_results, get_chunktext_results, visualize_schema
from src.chunkid_entities import get_entities_from_chunkids
from src.post_processing import create_vector_fulltext_indexes, create_entity_embedding, graph_schema_consolidation
from sse_starlette.sse import EventSourceResponse
from src.communities import create_communities
from src.neighbours import get_neighbour_nodes
import json
from typing import List, Optional
from google.oauth2.credentials import Credentials
from src.logger import CustomLogger
from datetime import datetime, timezone
import time
import gc
from Secweb.XContentTypeOptions import XContentTypeOptions
from Secweb.XFrameOptions import XFrame
from fastapi.middleware.gzip import GZipMiddleware
from src.ragas_eval import *
from starlette.types import ASGIApp, Receive, Scope, Send
from langchain_neo4j import Neo4jGraph
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from dotenv import load_dotenv
load_dotenv(override=True)
