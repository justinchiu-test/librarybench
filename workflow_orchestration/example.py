import time
import logging
import datetime
from workflow import (
    Task, Workflow, TaskFailedError, Schedule, ScheduleType
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("workflow_example")

def main():
    # Create a workflow with a name and logger
    workflow = Workflow(name="data_processing_workflow")
    workflow.set_logger(logger)
    
    # Define task functions that use context
    def fetch_data(context=None):
        """Fetch some data and return it in the context."""
        logger.info("Fetching data...")
        time.sleep(1)
        # Return context with new data
        context = context or {}
        context["data"] = [1, 2, 3, 4, 5]
        return context
    
    def process_data(context=None):
        """Process the data from the context."""
        context = context or {}
        data = context.get("data", [])
        logger.info(f"Processing data: {data}")
        time.sleep(1)
        
        # Process the data and update context
        context["processed"] = [x * 2 for x in data]
        return context
    
    def analyze_results(context=None):
        """Analyze the processed data from the context."""
        context = context or {}
        processed_data = context.get("processed", [])
        logger.info(f"Analyzing results: {processed_data}")
        time.sleep(1)
        
        # Analyze the data and update context
        context["analysis"] = sum(processed_data)
        return context
    
    def notify_success(context=None):
        """Send a notification about the completed analysis."""
        context = context or {}
        analysis = context.get("analysis")
        logger.info(f"Notification: Analysis complete with result {analysis}")
        
        # Update context with notification status
        context["notification"] = "sent"
        return context
    
    def flaky_task(context=None):
        """This task fails twice and succeeds on the third try, demonstrating retry with backoff."""
        context = context or {}
        
        # We need to track the attempts outside of the context since the context
        # is recreated on each execution
        attempts_so_far = getattr(flaky_task, 'attempts', 0) + 1
        setattr(flaky_task, 'attempts', attempts_so_far)
        
        logger.info(f"Running flaky task (real attempt {attempts_so_far})...")
        if attempts_so_far < 3:
            raise Exception(f"Flaky task failed on attempt {attempts_so_far}, will retry")
        
        context["flaky"] = "success"
        return context
    
    # Add tasks to workflow with dependencies
    data_task = Task(
        name="fetch_data",
        func=fetch_data
    )
    
    # Tasks can now use the context directly without wrappers
    process_task = Task(
        name="process_data", 
        func=process_data,
        dependencies=["fetch_data"]
    )
    
    analyze_task = Task(
        name="analyze_results", 
        func=analyze_results,
        dependencies=["process_data"]
    )
    
    notify_task = Task(
        name="notify_success", 
        func=notify_success,
        dependencies=["analyze_results"]
    )
    
    # Add flaky task with retries and exponential backoff
    flaky = Task(
        name="flaky_task",
        func=flaky_task,
        max_retries=3,
        retry_delay=0.5,  # Start with 0.5s delay
        retry_backoff=2.0,  # Double the delay on each retry
        dependencies=[]
    )
    
    # Add tasks to workflow
    workflow.add_task(data_task)
    workflow.add_task(process_task)
    workflow.add_task(analyze_task)
    workflow.add_task(notify_task)
    workflow.add_task(flaky)
    
    # Run the workflow
    try:
        print("\n=== Running workflow once ===")
        results = workflow.run()
        print("\nWorkflow completed successfully!")
        print("Results:")
        for task_name, result in results.items():
            print(f"- {task_name}: {result}")
            
        # Print execution times from history
        print("\nExecution History:")
        for i, execution in enumerate(workflow.execution_history):
            print(f"Run {i+1}: {execution.start_time} to {execution.end_time} - {execution.status}")
            print("Tasks:")
            for task_name, task_exec in execution.task_executions.items():
                duration = (task_exec.end_time - task_exec.start_time).total_seconds()
                print(f"  - {task_name}: {duration:.2f}s ({task_exec.status})")
        
        # Reset all tasks for another run
        for task in workflow.tasks.values():
            task.reset()
            
        # Demonstrate scheduled execution
        print("\n=== Scheduling workflow for hourly execution ===")
        # Set up an hourly schedule
        hourly_schedule = Schedule(type=ScheduleType.HOURLY)
        workflow.set_schedule(hourly_schedule)
        
        # Simulate time passing
        print("Current time: now")
        print(f"Should run: {workflow.should_run()}")  # Should be True for first run
        
        # Run the workflow
        if workflow.should_run():
            workflow.run()
            print("Workflow executed at initial time")
        
        # Simulate that only 30 minutes have passed
        print("\nTime now: now + 30 minutes")
        current_time = datetime.datetime.now() + datetime.timedelta(minutes=30)
        print(f"Should run: {workflow.should_run(current_time)}")  # Should be False
        
        # Simulate that a full hour has passed
        print("\nTime now: now + 1 hour")
        current_time = datetime.datetime.now() + datetime.timedelta(hours=1)
        print(f"Should run: {workflow.should_run(current_time)}")  # Should be True
        
        # Simulate running the workflow at the later time
        if workflow.should_run(current_time):
            # Reset all tasks for the demonstration
            for task in workflow.tasks.values():
                task.reset()
            print("Workflow would execute again after 1 hour")
        
    except TaskFailedError as e:
        print(f"Workflow failed: {e}")
        # Print status of all tasks
        print("\nTask statuses:")
        for task_name, task in workflow.tasks.items():
            status = f"{task.state.value}"
            if task.error:
                status += f" (Error: {task.error})"
            print(f"- {task_name}: {status}")
            
        # Print execution logs
        if task.execution_records:
            print(f"\nExecution logs for {task_name}:")
            for log in task.execution_records[-1].logs:
                print(f"  {log}")

if __name__ == "__main__":
    main()