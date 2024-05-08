# Azure Storage Utilities for Data Operations

## Configure Environment Variables

Before you begin utilising the scripts, you must configure the necessary environment variables. These variables will be used to access Azure Blob Storage.

### Setting Up Environment Variables on Linux and macOS

Open your terminal.
Open your `.bashrc` file in a text editor. You can use `nano` by typing

```bash
nano ~/.bashrc
```

Add the following lines at the end of the .bashrc file to set your environment variables

```bash
   export STORAGE_SAS_TOKEN_CHD="sas_token_placeholder"
   export CONTAINER_NAME_CHD="container_name_placeholder"
   export STORAGE_ACCOUNT_CHD="storage_account_placeholder"
   ```

   Replace sas_token_placeholder, container_name_placeholder, and storage_account_placeholder with your actual Azure Blob Storage details.

Save and close the editor. If you're using nano, you can do this by pressing CTRL+X, then Y to confirm, and Enter to save.

Update your current session with the changes by sourcing the .bashrc file

```bash
   source ~/.bashrc
   ```
