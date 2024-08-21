const apiUrl = 'http://localhost:5000';
let users = {};
let currentUserId = null;

document.addEventListener('DOMContentLoaded', function() {
    updateUserList();
});

async function addUser() {
    const fullName = document.getElementById('full-name').value.trim();
    const username = document.getElementById('username').value.trim();
    if (!fullName || !username) return alert('Both full name and username are required');

    try {
        const response = await fetch(`${apiUrl}/add-user`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ fullName, username })
        });
        if (!response.ok) throw new Error('Failed to add user');
        const user = await response.json();
        users[user.id] = { fullName: user.fullName, username: user.username };
        updateUserList();
        clearForm();
    } catch (error) {
        console.error('Error adding user:', error);
        alert('Error adding user. Please try again.');
    }
}

async function updateUser() {
    if (currentUserId === null) return alert('No user selected');

    const newFullName = document.getElementById('update-full-name').value.trim();
    const newUsername = document.getElementById('update-username').value.trim();
    if (!newFullName || !newUsername) return alert('Both new full name and new username are required');

    try {
        const response = await fetch(`${apiUrl}/update-user/${currentUserId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ fullName: newFullName, username: newUsername })
        });
        if (!response.ok) throw new Error('Failed to update user');
        users[currentUserId] = { fullName: newFullName, username: newUsername };
        updateUserList();
        clearForm();
        document.getElementById('user-actions').style.display = 'none';
        currentUserId = null;
    } catch (error) {
        console.error('Error updating user:', error);
        alert('Error updating user. Please try again.');
    }
}

async function updateUserByUsername() {
    const oldUsername = document.getElementById('old-username').value.trim();
    const newFullName = document.getElementById('update-full-name').value.trim();
    const newUsername = document.getElementById('update-username').value.trim();

    if (!oldUsername || !newFullName || !newUsername) return alert('Old username, new full name, and new username are required');

    try {
        const response = await fetch(`${apiUrl}/update-user-by-username?oldUsername=${encodeURIComponent(oldUsername)}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ fullName: newFullName, username: newUsername })
        });
        if (!response.ok) throw new Error('Failed to update user');
        updateUserList();
        clearForm();
        document.getElementById('user-actions').style.display = 'none';
    } catch (error) {
        console.error('Error updating user:', error);
        alert('Error updating user. Please try again.');
    }
}

async function deleteUser() {
    if (currentUserId === null) return alert('No user selected');

    try {
        const response = await fetch(`${apiUrl}/delete-user?id=${currentUserId}`, {
            method: 'DELETE'
        });
        if (!response.ok) throw new Error('Failed to delete user');
        delete users[currentUserId];
        updateUserList();
        clearForm();
        document.getElementById('user-actions').style.display = 'none';
        currentUserId = null;
    } catch (error) {
        console.error('Error deleting user:', error);
        alert('Error deleting user. Please try again.');
    }
}

async function updateUserList() {
    try {
        const response = await fetch(`${apiUrl}/users`);
        if (!response.ok) throw new Error('Failed to fetch users');
        const userList = await response.json();
        const ul = document.getElementById('user-list-ul');
        ul.innerHTML = ''; // Clear the list

        // Clear the local users object
        users = {};

        for (const user of userList) {
            if (user.id && user.fullName && user.username) {
                users[user.id] = { fullName: user.fullName, username: user.username };
                const li = document.createElement('li');
                li.textContent = `${user.fullName} (${user.username}) - ID: ${user.id}`;
                li.onclick = () => selectUser(user.id);
                ul.appendChild(li);
            } else {
                console.error('Invalid user data:', user);
            }
        }
        document.getElementById("no-users").style.display = userList.length ? 'none' : 'block';
    } catch (error) {
        console.error('Error updating user list:', error);
        document.getElementById("no-users").innerHTML = "No users found";
    }
}

function selectUser(userId) {
    currentUserId = userId;
    document.getElementById('update-full-name').value = users[userId].fullName;
    document.getElementById('update-username').value = users[userId].username;
    document.getElementById('user-actions').style.display = 'block';
}

function clearForm() {
    document.getElementById('full-name').value = '';
    document.getElementById('username').value = '';
    document.getElementById('update-full-name').value = '';
    document.getElementById('update-username').value = '';
    document.getElementById('old-username').value = ''; // Ensure old-username field is cleared
}
