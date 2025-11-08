from fastapi import FastAPI, File, UploadFile, HTTPException
from typing_extensions import Annotated
import uvicorn
from utils import *
from dijkstra import dijkstra

# create FastAPI app
app = FastAPI()

# global variable for active graph
active_graph = None

@app.get("/")
async def root():
    return {"message": "Welcome to the Shortest Path Solver!"}

@app.post("/upload_graph_json/")
async def create_upload_file(file: UploadFile):  # runs asynchronously (https://fastapi.tiangolo.com/async/#in-a-hurry)
    global active_graph
    if not file.filename.endswith(".json"):
        return {"Upload Error": "Invalid file type"} # must be JSON file
    try:
        active_graph = create_graph_from_json(file) # convert to graph (utils.py function)
        return {"Upload Success": file.filename} # returns filename
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process graph: {str(e)}") # other errors

@app.get("/solve_shortest_path/start_node_id={start_node_id}&end_node_id={end_node_id}")
async def get_shortest_path(start_node_id: str, end_node_id: str):
    global active_graph
    if active_graph is None:
        return {"Solver Error": "No active graph, please upload a graph first."} # no graph was uploaded
    start_node_id = str(start_node_id).strip() # convert ids (ints) to strings
    end_node_id = str(end_node_id).strip() # convert ids (ints) to strings
    if start_node_id not in active_graph.nodes or end_node_id not in active_graph.nodes:
        return {"Solver Error": "Invalid start or end node ID."} # the start or end node ID does not exist
    try:
        start_node = active_graph.nodes[start_node_id] # start node
        dijkstra(active_graph, start_node) # run dijkstra

        # Create list of the shortest path
        path = []
        current = active_graph.nodes[end_node_id]
        while current:
            path.append(current.id)
            current = current.prev
        path.reverse()
        total_distance = active_graph.nodes[end_node_id].dist
        return {
            "shortest_path": path, # returns shortest path
            "total_distance": total_distance # returns distance
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error computing shortest path: {str(e)}") # other errors

if __name__ == "__main__":
    print("Server is running at http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)
    