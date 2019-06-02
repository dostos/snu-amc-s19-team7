from .test_client import *
import asyncio

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test environment for a GroupPowerSaveServer.')
    parser.add_argument('--test', 
    type=str, 
    choices=test_classes.keys(), 
    default=RoleUpdateTest.__name__,
    help='Name of the test function')
    parser.add_argument('--target_server', 
    type=str,
    default='http://localhost:8080/')
    parser.add_argument('--num_clients',
    type=int,
    default=10)

    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(execute(loop, test_classes[args.test], args.num_clients, args.target_server, lambda clients: print(clients)))
    loop.close()