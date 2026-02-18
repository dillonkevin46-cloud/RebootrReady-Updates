from waitress import serve
from config.wsgi import application

if __name__ == '__main__':
    print("-------------------------------------------------------")
    print("RebootReady is running on http://0.0.0.0:8001")
    print("Press Ctrl+C to stop.")
    print("-------------------------------------------------------")
    
    # 0.0.0.0 allows access from other computers on the network
    serve(application, host='0.0.0.0', port=8001, threads=6)