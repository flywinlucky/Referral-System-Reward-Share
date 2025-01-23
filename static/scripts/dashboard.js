function copyToClipboard(referralLink) {
    navigator.clipboard.writeText(referralLink).then(() => {
        const notification = document.getElementById('notification');
        notification.style.display = 'block';
        setTimeout(() => {
            notification.style.display = 'none';
        }, 2000);
    });
}

function openModal() {
    document.getElementById("myModal").style.display = "block";
}

function closeModal() {
    document.getElementById("myModal").style.display = "none";
}

function openEditModal(linkName, redirectLink, revenueShare, referralId) {
    document.getElementById("editLinkName").value = linkName;
    document.getElementById("editRedirectLink").value = redirectLink;
    document.getElementById("editRevenueShare").value = revenueShare;
    document.getElementById("editReferralId").value = referralId;
    document.getElementById("editModal").style.display = "block";
}

function closeEditModal() {
    document.getElementById("editModal").style.display = "none";
}
