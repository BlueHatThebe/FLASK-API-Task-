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
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to add user');
        }
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
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to update user');
        }
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

async function deleteUser() {
    if (currentUserId === null) return alert('No user selected');

    try {
        const response = await fetch(`${apiUrl}/delete-user?id=${currentUserId}`, {
            method: 'DELETE'
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to delete user');
        }
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
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to fetch users');
        }

        const usersArray = await response.json();
        users = {};  // Clear existing users
        const ul = document.getElementById('user-list');
        ul.innerHTML = ''; // Clear existing list

        if (usersArray.length === 0) {
            document.getElementById('no-users').style.display = 'block';
            return;
        }

        document.getElementById('no-users').style.display = 'none';

        for (const user of usersArray) {
            if (user.id && user.fullName && user.username) {
                users[user.id] = { fullName: user.fullName, username: user.username };
                const li = document.createElement('li');
                li.textContent = `${user.fullName} (@${user.username})`;
                li.addEventListener('click', () => selectUser(user.id));
                ul.appendChild(li);
            } else {
                console.error('Invalid user data:', user);
            }
        }
    } catch (error) {
        console.error('Error updating user list:', error);
        document.getElementById('no-users').textContent = "No users found";
        document.getElementById('no-users').style.display = 'block';
    }
}

function selectUser(id) {
    // Clear previously selected item
    const ul = document.getElementById('user-list');
    const items = ul.querySelectorAll('li');
    items.forEach(item => item.classList.remove('selected'));

    if (users[id]) {
        document.getElementById('update-full-name').value = users[id].fullName;
        document.getElementById('update-username').value = users[id].username;
        document.getElementById('user-actions').style.display = 'block';
        currentUserId = id;

        // Add underline to the selected user
        const selectedItem = Array.from(items).find(item => item.textContent.includes(users[id].fullName));
        if (selectedItem) {
            selectedItem.classList.add('selected');
        }
    }
}

function clearForm() {
    document.getElementById('full-name').value = '';
    document.getElementById('username').value = '';
    document.getElementById('update-full-name').value = '';
    document.getElementById('update-username').value = '';
}
