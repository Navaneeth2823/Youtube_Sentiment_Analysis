document.getElementById('analyze-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const videoUrl = document.getElementById('video_url').value;
     document.getElementById('loading').style.display = 'block';  // Show loader
    document.getElementById('results').style.display = 'none';   // Hide previous results if any

    fetch('/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: 'video_url=' + encodeURIComponent(videoUrl)
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById('loading').style.display = 'none';  // Hide loader
        if (data.error) {
            alert(data.error);
            return;
        }
        document.getElementById('results').style.display = 'block';
        document.getElementById('total').textContent = data.stats.total;
        showHistogram(data.stats, data.sentiment);
    })
    .catch(err => {
        document.getElementById('loading').style.display = 'none';  // Hide loader
        alert('Something went wrong. Please try again.');
        console.error(err);
    });
});

function showHistogram(stats, sentiment) {
    const ctx = document.getElementById('histogram').getContext('2d');
    if (window.histChart) window.histChart.destroy();
    window.histChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Good', 'Bad', 'Neutral'],
            datasets: [{
                label: 'Comments',
                data: [stats.good, stats.bad, stats.neutral],
                backgroundColor: ['#12e119ff', '#e31708ff', '#fbf3f3ff']
            }]
        },
        options: {
            onClick: function(evt, elements) {
                if (elements.length > 0) {
                    const idx = elements[0].index;
                    let type = ['good', 'bad', 'neutral'][idx];
                    showComments(type, sentiment[type]);
                }
            }
        }
    });
}

function showComments(type, comments) {
    const list = document.getElementById('comments-list');
    list.innerHTML = `<h3>${type.charAt(0).toUpperCase() + type.slice(1)} Comments (${comments.length})</h3>`;
    list.innerHTML += '<ul>' + comments.map(c => `<li>${c}</li>`).join('') + '</ul>';
}
