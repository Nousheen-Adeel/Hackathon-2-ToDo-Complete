# Prompt History Record: API PUT and DELETE Endpoints Implementation

**Date**: Sunday, 28 December 2025  
**Task**: Implement PUT and DELETE endpoints in src/api.py  
**Description**: Implementation of the PUT and DELETE endpoints for updating and deleting tasks in the Todo API

## Actions Taken:
1. Created TaskUpdate Pydantic model with:
   - title (str) field
   - description (str) field with default value of empty string
2. Implemented PUT /tasks/{id} endpoint that:
   - Accepts an integer ID as path parameter
   - Accepts a TaskUpdate object as request body
   - Calls services.update_task(id, task_data.title, task_data.description)
   - Returns the updated task with 200 OK status if successful
   - Raises 404 Not Found error if the task doesn't exist
3. Implemented DELETE /tasks/{id} endpoint that:
   - Accepts an integer ID as path parameter
   - Calls services.delete_task(id)
   - Returns a success message with 200 OK status if successful
   - Raises 404 Not Found error if the task doesn't exist
4. Added proper type hints, status codes, and documentation
5. Imported HTTPException for proper error handling

## Results:
- TaskUpdate Pydantic model is properly defined with required fields
- PUT /tasks/{id} endpoint is implemented and functional
- DELETE /tasks/{id} endpoint is implemented and functional
- Proper error handling is implemented for both endpoints
- 404 Not Found status codes are returned when tasks don't exist
- Both endpoints integrate correctly with the existing service layer
- Type hints and documentation are included for both endpoints

## Files Modified:
- src/api.py (updated with PUT and DELETE endpoints)

## Next Steps:
- Implement the PATCH endpoint for toggling task status
- Add comprehensive tests for all implemented endpoints
- Consider creating additional Pydantic models if needed for other endpoints