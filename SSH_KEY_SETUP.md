# SSH Key Setup Guide for Contabo VPS

This guide will help you set up passwordless SSH authentication for your Contabo VPS, making deployments seamless.

## 🚀 Quick Setup (Automated)

```bash
./setup_ssh_key.sh
```

This script will:
1. ✅ Check for existing SSH key or create a new one
2. ✅ Copy the key to your VPS
3. ✅ Test the connection
4. ✅ Save VPS configuration

**Time Required:** 2-3 minutes

---

## 📋 Manual Setup (If Preferred)

### Step 1: Check for Existing SSH Key

```bash
ls -la ~/.ssh/id_rsa.pub
```

**If key exists:**
- Skip to Step 3

**If key doesn't exist:**
- Continue to Step 2

### Step 2: Generate New SSH Key

```bash
# Generate a new RSA key (4096 bits)
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"

# Press Enter to accept default location (~/.ssh/id_rsa)
# Press Enter twice to skip passphrase (or set one if you prefer)
```

**Result:** Creates two files:
- `~/.ssh/id_rsa` - Private key (keep secret!)
- `~/.ssh/id_rsa.pub` - Public key (safe to share)

### Step 3: View Your Public Key

```bash
cat ~/.ssh/id_rsa.pub
```

Copy this entire output. You'll need it in the next step.

### Step 4: Copy Key to VPS

**Option A: Using ssh-copy-id (Easiest)**

```bash
ssh-copy-id nicksriv@213.199.48.187
```

Enter your VPS password when prompted. Done!

**Option B: Manual Method (If ssh-copy-id not available)**

```bash
# Copy key to VPS
cat ~/.ssh/id_rsa.pub | ssh nicksriv@213.199.48.187 "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

Enter your VPS password when prompted.

**Option C: Using VPS Control Panel**

1. Log into your Contabo control panel
2. Navigate to your VPS → SSH Keys
3. Click "Add SSH Key"
4. Paste the contents of `~/.ssh/id_rsa.pub`
5. Save

### Step 5: Test SSH Connection

```bash
# Test without password
ssh nicksriv@213.199.48.187

# If successful, you should log in without password prompt!
```

### Step 6: Configure Deployment Scripts

```bash
# Create VPS config file
cat > .vps_config << EOF
VPS_IP=213.199.48.187
SSH_USER=nicksriv
EOF
```

---

## 🔧 Troubleshooting

### Problem: "Permission denied (publickey)"

**Solution 1: Check VPS permissions**
```bash
ssh nicksriv@213.199.48.187 'chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys'
```

**Solution 2: Verify key is in authorized_keys**
```bash
ssh nicksriv@213.199.48.187 'cat ~/.ssh/authorized_keys'
```
Your public key should be listed here.

**Solution 3: Check SSH config on VPS**
```bash
ssh nicksriv@213.199.48.187
sudo nano /etc/ssh/sshd_config
```

Ensure these lines are set:
```
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
```

Restart SSH:
```bash
sudo systemctl restart sshd
```

### Problem: "Connection refused"

**Check if SSH service is running:**
```bash
# From VPS (log in with password)
sudo systemctl status sshd
sudo systemctl start sshd
```

### Problem: "Host key verification failed"

**Remove old host key:**
```bash
ssh-keygen -R 213.199.48.187
```

Then try connecting again.

### Problem: Still asks for password

**Check verbose SSH output:**
```bash
ssh -v nicksriv@213.199.48.187
```

Look for errors related to:
- Key file permissions
- Authentication methods
- Server configuration

---

## 🔒 Security Best Practices

### 1. Protect Your Private Key

```bash
# Ensure correct permissions
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
```

### 2. Use a Passphrase (Optional but Recommended)

When generating the key, set a passphrase:
```bash
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"
# Enter a strong passphrase when prompted
```

Then use ssh-agent to avoid typing it repeatedly:
```bash
# Start ssh-agent
eval "$(ssh-agent -s)"

# Add key to agent
ssh-add ~/.ssh/id_rsa

# On macOS, add to keychain (remembers across reboots)
ssh-add --apple-use-keychain ~/.ssh/id_rsa
```

### 3. Disable Password Authentication on VPS (After SSH Key Works)

```bash
# SSH into VPS
ssh nicksriv@213.199.48.187

# Edit SSH config
sudo nano /etc/ssh/sshd_config

# Change this line:
PasswordAuthentication no

# Save and restart
sudo systemctl restart sshd
```

**Warning:** Only do this AFTER confirming SSH key authentication works!

---

## 📱 Using Multiple Computers

If you want to deploy from multiple computers:

### Option 1: Copy Same Key to All Computers

```bash
# On computer 1 (has the key)
cat ~/.ssh/id_rsa.pub

# On computer 2 (needs the key)
# Copy the private key (SECURE METHOD ONLY)
scp user@computer1:~/.ssh/id_rsa ~/.ssh/
scp user@computer1:~/.ssh/id_rsa.pub ~/.ssh/
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
```

### Option 2: Generate Separate Keys (More Secure)

```bash
# On each computer, generate a new key
ssh-keygen -t rsa -b 4096 -C "computer2@example.com"

# Copy each key to VPS
ssh-copy-id nicksriv@213.199.48.187
```

VPS will accept multiple keys in `~/.ssh/authorized_keys`.

---

## 🎯 Quick Reference

### Check if SSH Key Exists
```bash
ls -la ~/.ssh/id_rsa.pub
```

### Generate New SSH Key
```bash
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"
```

### View Public Key
```bash
cat ~/.ssh/id_rsa.pub
```

### Copy Key to VPS
```bash
ssh-copy-id nicksriv@213.199.48.187
```

### Test Connection
```bash
ssh nicksriv@213.199.48.187
```

### Fix Permissions
```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
chmod 600 ~/.ssh/authorized_keys  # On VPS
```

---

## ✅ Verification Checklist

Before proceeding with deployment:

- [ ] SSH key generated or exists
- [ ] Public key copied to VPS
- [ ] Can SSH without password: `ssh nicksriv@213.199.48.187`
- [ ] VPS config saved in `.vps_config`
- [ ] Deployment scripts are executable

---

## 🚀 After SSH Key Setup

Once SSH key authentication is working, you can:

### Run Initial Deployment
```bash
./deploy_interactive.sh
```

### Deploy Updates
```bash
./update_deployment.sh
```

### Check Status
```bash
./check_status.sh
```

All scripts will now work without password prompts! 🎉

---

## 💡 Tips

1. **Backup Your Key**
   ```bash
   cp ~/.ssh/id_rsa ~/Backups/ssh_key_backup
   cp ~/.ssh/id_rsa.pub ~/Backups/ssh_key_backup.pub
   ```

2. **Use SSH Config for Convenience**
   ```bash
   # Edit SSH config
   nano ~/.ssh/config
   
   # Add this:
   Host contabo-vps
       HostName 213.199.48.187
       User nicksriv
       IdentityFile ~/.ssh/id_rsa
   
   # Now you can simply:
   ssh contabo-vps
   ```

3. **Test Specific Key**
   ```bash
   ssh -i ~/.ssh/id_rsa nicksriv@213.199.48.187
   ```

---

## 🆘 Still Having Issues?

Run the automated setup script with verbose output:

```bash
./setup_ssh_key.sh
```

Or contact me with the output of:
```bash
ssh -v nicksriv@213.199.48.187
```

---

## 📞 Summary

**Easiest Method:**
```bash
./setup_ssh_key.sh
```

**Manual Method:**
```bash
# 1. Generate key (if needed)
ssh-keygen -t rsa -b 4096

# 2. Copy to VPS
ssh-copy-id nicksriv@213.199.48.187

# 3. Test
ssh nicksriv@213.199.48.187

# 4. Deploy!
./deploy_interactive.sh
```

**Time:** 2-3 minutes  
**Benefit:** Passwordless deployment forever! 🎉
