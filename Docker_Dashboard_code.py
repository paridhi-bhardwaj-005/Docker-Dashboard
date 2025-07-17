import streamlit as st
import paramiko

# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(page_title="Docker Dashboard", page_icon="🐳", layout="centered")
st.title("🐳 Docker Management Dashboard")
st.image("https://www.docker.com/wp-content/uploads/2022/03/Moby-logo.png", width=200)

# -------------------------------
# Session State for SSH
# -------------------------------
if "ssh_client" not in st.session_state:
    st.session_state.ssh_client = None
if "ssh_connected" not in st.session_state:
    st.session_state.ssh_connected = False

# -------------------------------
# Sidebar SSH Login
# -------------------------------
st.sidebar.title("SSH Login")
ssh_host = st.sidebar.text_input("SSH Host")
ssh_user = st.sidebar.text_input("SSH Username")
ssh_pass = st.sidebar.text_input("SSH Password", type="password")
connect_btn = st.sidebar.button("Connect via SSH")

if connect_btn:
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ssh_host, username=ssh_user, password=ssh_pass)
        st.session_state.ssh_client = client
        st.session_state.ssh_connected = True
        st.sidebar.success("SSH Connected!")
    except Exception as e:
        st.sidebar.error(f"SSH connection failed: {e}")

# -------------------------------
# Helper Function to Run Commands via SSH
# -------------------------------
def run_command(command):
    if not st.session_state.ssh_connected or not st.session_state.ssh_client:
        st.error("Not connected to SSH server.")
        return None
    try:
        stdin, stdout, stderr = st.session_state.ssh_client.exec_command(' '.join(command))
        out = stdout.read().decode()
        err = stderr.read().decode()

        class Result:
            def __init__(self, stdout, stderr):
                self.stdout = stdout
                self.stderr = stderr
                self.returncode = 0 if not err else 1

        return Result(out, err)

    except Exception as e:
        st.error(f"Command failed: {e}")
        return None

# -------------------------------
# Main Page Description
# -------------------------------
st.subheader("What is Docker?")
st.markdown("""
Docker is an open platform for developing, shipping, and running applications inside lightweight, portable, and self-sufficient containers.

**Key Concepts:**
- **Image**: A snapshot/template of an application environment.
- **Container**: A running instance of an image.
- **Dockerfile**: Instructions to build an image.
- **Docker Hub**: Public repository for Docker images.

**Why Docker?**
- Consistent environments
- Fast deployment
- Secure isolation
- Perfect for microservices and CI/CD
""")

st.markdown("---")
st.subheader("About This Project")
st.markdown("""
This **Docker Dashboard** allows you to control Docker on any remote machine via SSH — pull images, launch containers, stop/remove them, and inspect images — all from your browser!
""")
st.markdown("---")

# -------------------------------
# Docker Operations
# -------------------------------
operation = st.selectbox("Select Docker Operation", [
    "Pull image from Docker Hub",
    "Launch a new container",
    "List running containers",
    "Stop a container",
    "Remove a container",
    "List all Docker images"
])

st.markdown("---")

# Operation Logic
if operation == "Pull image from Docker Hub":
    st.subheader("🔧 Pull Docker Image")
    image_to_pull = st.text_input("Docker Image to Pull", value="nginx")
    if st.button("Pull Image"):
        if image_to_pull.strip():
            result = run_command(["docker", "pull", image_to_pull])
            if result:
                if result.returncode == 0:
                    st.success("Image pulled successfully!")
                    st.code(result.stdout)
                else:
                    st.error("Pull failed")
                    st.code(result.stderr)
        else:
            st.error("Please enter an image name.")

elif operation == "Launch a new container":
    st.subheader("Launch Docker Container")
    with st.form("launch_form"):
        container_image = st.text_input("Image Name", value="nginx")
        container_name = st.text_input("Container Name (optional)")
        port_map = st.text_input("Port Mapping (e.g. 8080:80)", value="")
        detached_mode = st.checkbox("Detached Mode (-d)", value=True)
        launch_submit = st.form_submit_button("Launch")

        if launch_submit:
            cmd = ["docker", "run"]
            if detached_mode:
                cmd.append("-d")
            if container_name:
                cmd += ["--name", container_name]
            if port_map:
                cmd += ["-p", port_map]
            cmd.append(container_image)
            result = run_command(cmd)
            if result:
                if result.returncode == 0:
                    st.success(f"Container launched successfully!\n\n```\n{result.stdout}```")
                else:
                    st.error(f"Launch failed:\n\n```\n{result.stderr}```")
                    

elif operation == "List running containers":
    st.subheader("Running Containers")
    if st.button("Show Running Containers"):
        result = run_command(["docker", "ps"])
        if result:
            st.code(result.stdout or result.stderr)

elif operation == "Stop a container":
    st.subheader("Stop a Container")
    stop_container = st.text_input("Container Name or ID to Stop")
    if st.button("Stop Container"):
        if stop_container:
            result = run_command(["docker", "stop", stop_container])
            if result:
                if result.returncode == 0:
                    st.success("Container stopped.")
                    st.code(result.stdout)
                else:
                    st.error("Failed to stop.")
                    st.code(result.stderr)
        else:
            st.error("Enter container name or ID.")

elif operation == "Remove a container":
    st.subheader("Remove a Container")
    remove_container = st.text_input("Container Name or ID to Remove")
    if st.button("Remove Container"):
        if remove_container:
            result = run_command(["docker", "rm", remove_container])
            if result:
                if result.returncode == 0:
                    st.success("Container removed.")
                    st.code(result.stdout)
                else:
                    st.error("Failed to remove.")
                    st.code(result.stderr)
        else:
            st.error("Enter container name or ID.")

elif operation == "List all Docker images":
    st.subheader("Local Docker Images")
    if st.button("List Docker Images"):
        result = run_command(["docker", "images"])
        if result:
            st.code(result.stdout or result.stderr)
