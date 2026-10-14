const form = document.getElementById("leaveForm");
const list = document.getElementById("leaveList");
const count = document.getElementById("applicationCount");
const emptyMessage = document.getElementById("emptyMessage");

let applications = [];
let nextId = 1;

form.addEventListener("submit", function (event) {
    event.preventDefault();

    const name = document.getElementById("employeeName").value.trim();
    const type = document.getElementById("leaveType").value;
    const from = document.getElementById("fromDate").value;
    const to = document.getElementById("toDate").value;
    const reason = document.getElementById("reason").value.trim();

    if (!name || !reason || !from || !to) {
        alert("Please fill in all fields.");
        return;
    }

    if (to < from) {
        alert("To Date cannot be earlier than From Date.");
        return;
    }

    applications.push({
        id: nextId++,
        name: name,
        type: type,
        from: from,
        to: to,
        reason: reason,
        status: "Pending"
    });

    renderApplications();
    form.reset();
});

function renderApplications() {
    list.replaceChildren();

    applications.forEach(function (app) {
        const row = document.createElement("tr");

        function addCell(value) {
            const cell = document.createElement("td");
            cell.textContent = value;
            row.appendChild(cell);
            return cell;
        }

        addCell(app.name);
        addCell(app.type);
        addCell(app.from);
        addCell(app.to);
        addCell(app.reason);

        const statusCell = addCell(app.status);
        statusCell.className = "status " + app.status.toLowerCase();

        const actionCell = document.createElement("td");

        if (app.status === "Pending") {
            const approveButton = document.createElement("button");
            approveButton.textContent = "Approve";
            approveButton.className = "approve";

            approveButton.addEventListener("click", function () {
                updateStatus(app.id, "Approved");
            });

            const rejectButton = document.createElement("button");
            rejectButton.textContent = "Reject";
            rejectButton.className = "reject";

            rejectButton.addEventListener("click", function () {
                updateStatus(app.id, "Rejected");
            });

            actionCell.append(approveButton, rejectButton);
        } else {
            actionCell.textContent = "Decision recorded";
        }

        row.appendChild(actionCell);
        list.appendChild(row);
    });

    count.textContent = "Total applications: " + applications.length;
    emptyMessage.style.display =
        applications.length === 0 ? "block" : "none";
}

function updateStatus(id, newStatus) {
    applications = applications.map(function (app) {
        if (app.id === id && app.status === "Pending") {
            return { ...app, status: newStatus };
        }
        return app;
    });

    renderApplications();
}