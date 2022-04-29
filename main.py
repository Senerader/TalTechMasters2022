import logging
import coloredlogs
from Core.globals import EXIT_APP_EVENT
from StableBaselines.full_stack_agent import run_full_stack_agent
from DrlPlatform import UdpServer

if __name__ == "__main__":
    coloredlogs.install(level="INFO")
    logging.getLogger().setLevel(logging.INFO)
    logger = logging.getLogger(__name__)
    # Establish server for env connection
    env_server = UdpServer(
        server_host="localhost",
        server_port=16385,
        client_host="localhost",
        client_port=16384
    )
    # Start inference agent
    try:
        logger.info("Starting environment server. Waiting for connection...")
        env_server.start_server()
        run_full_stack_agent(env_server)
    except KeyboardInterrupt:
        EXIT_APP_EVENT.set()
    except Exception as err:
        logger.error("Received error, %s", str(err))
        EXIT_APP_EVENT.set()
        raise err
    finally:
        env_server.close_server()
